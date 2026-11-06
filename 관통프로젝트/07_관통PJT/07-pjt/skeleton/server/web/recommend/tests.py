import base64
import io
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import requests
from PIL import Image
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import RecommendationForm
from .models import Recommendation, ImageAnalysis

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'proxy'))
import main as proxy
from schemas import ChatRequest, ImageGenerationRequest, ImageAnalysisRequest


def response(data=None, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


class WebTests(TestCase):
    def test_all_input_pages(self):
        for name in ['form', 'text', 'route', 'image', 'analyze', 'flow']:
            with self.subTest(name=name):
                self.assertContains(self.client.get(reverse('recommend:' + name)), 'csrfmiddlewaretoken')

    def test_form_validation(self):
        for text in ['', '   ', 'a' * 301]:
            self.assertFalse(RecommendationForm({'request_text': text}).is_valid())
        self.assertTrue(RecommendationForm({'request_text': 'a' * 300}).is_valid())
        self.client.post(reverse('recommend:form'), {'request_text': 'novel'})
        self.assertEqual(Recommendation.objects.get().request_text, 'novel')



    @patch('recommend.views.requests.post')
    def test_rejected_and_unavailable(self, post):
        for status in [403, 503]:
            post.return_value = response(status=status)
            page = self.client.post(reverse('recommend:text'), {'request_text': 'request'})
            self.assertEqual(page.status_code, status)
        post.side_effect = requests.ConnectionError()
        page = self.client.post(reverse('recommend:text'), {'request_text': 'request'})
        self.assertEqual(page.status_code, 503)
        self.assertEqual(Recommendation.objects.count(), 0)

    @patch('recommend.views.requests.post')
    def test_flow_branches(self, post):
        for route, data in [('/chat/completions', {'content': '추천 결과', 'model_used': 'gpt-5-nano'}), ('/images/generations', {'image_base64': 'aW1hZ2U='})]:
            post.side_effect = [response({'route': route}), response(data)]
            page = self.client.post(reverse('recommend:flow'), {'request_text': 'request'})
            self.assertEqual(page.status_code, 200)
            self.assertTrue(post.call_args.args[0].endswith(route))
            self.assertEqual(Recommendation.objects.latest('id').route, route)
        post.side_effect = [response({'route': '/chat/completions'}), response(status=403)]
        self.assertEqual(self.client.post(reverse('recommend:flow'), {'request_text': 'request'}).status_code, 403)
        post.side_effect = [response(status=503)]
        self.assertEqual(self.client.post(reverse('recommend:flow'), {'request_text': 'request'}).status_code, 503)

    @patch('recommend.views.requests.post')
    def test_inline_image_and_upload_analysis(self, post):
        image = io.BytesIO()
        Image.new('RGB', (2, 2), 'white').save(image, format='JPEG')
        image_bytes = image.getvalue()
        encoded = base64.b64encode(image_bytes).decode()
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            post.return_value = response({'image_base64': encoded})
            page = self.client.post(reverse('recommend:image'), {'request_text': 'cover'})
            result = Recommendation.objects.get()
            self.assertFalse(result.image)
            self.assertContains(page, 'data:image/jpeg;base64,' + encoded)
            post.return_value = response({'content': '표지 분석 결과'})
            upload = SimpleUploadedFile('cover.jpg', image_bytes, content_type='image/jpeg')
            page = self.client.post(reverse('recommend:analyze'), {'question': 'analyze', 'image': upload})
            self.assertContains(page, '표지 분석 결과')
            self.assertEqual(post.call_args.kwargs['json']['image_base64'], encoded)
            self.assertEqual(ImageAnalysis.objects.get().content, '표지 분석 결과')



class ProxyTests(SimpleTestCase):
    @patch.object(proxy, 'ask_gms')
    def test_guardrail_stops_all_generation(self, ask):
        ask.return_value = '{"is_appropriate": false}'
        calls = [
            (proxy.chat_completions, ChatRequest(messages=[{'role': 'user', 'content': 'request'}])),
            (proxy.image_generations, ImageGenerationRequest(prompt='request')),
            (proxy.image_analysis, ImageAnalysisRequest(question='request', image_base64='')),
        ]
        for function, data in calls:
            ask.reset_mock()
            with self.assertRaises(proxy.HTTPException) as error:
                function(data)
            self.assertEqual(error.exception.status_code, 403)
            self.assertEqual(ask.call_count, 1)
            self.assertEqual(ask.call_args.args[2]['json_schema']['schema']['properties']['is_appropriate']['type'], 'boolean')




    @patch.object(proxy, 'ask_gms')
    def test_image_analysis_data_uri(self, ask):
        for raw, mime in [(b'\xff\xd8\xff', 'jpeg'), (b'\x89PNG', 'png')]:
            encoded = base64.b64encode(raw).decode()
            ask.side_effect = ['{"is_appropriate": true}', 'analysis']
            proxy.image_analysis(ImageAnalysisRequest(question='analyze', image_base64=encoded))
            content = ask.call_args.args[0][1]['content']
            self.assertEqual(content[0]['image_url']['url'], 'data:image/' + mime + ';base64,' + encoded)

    @patch.object(proxy, 'GMS_KEY', 'test-key')
    @patch.object(proxy, 'GMS_URL', 'https://example.invalid/v1')
    @patch.object(proxy.requests, 'post')
    def test_upstream_errors_and_guardrail_failure(self, post):
        for failure in [response(status=401), requests.Timeout()]:
            post.side_effect = None
            post.return_value = failure
            if isinstance(failure, Exception):
                post.side_effect = failure
            with self.assertRaises(proxy.HTTPException) as error:
                proxy.chat_completions(ChatRequest(messages=[{'role': 'user', 'content': 'request'}]))
            self.assertEqual(error.exception.status_code, 503)
            self.assertEqual(post.call_args.kwargs['timeout'], 120)


    @patch.object(proxy, 'gms_post')
    @patch.object(proxy, 'ensure_appropriate')
    def test_image_generation(self, guardrail, post):
        post.return_value = response({'data': [{'b64_json': 'aW1hZ2U='}]})
        self.assertEqual(proxy.image_generations(ImageGenerationRequest(prompt='cover'))['image_base64'], 'aW1hZ2U=')
        guardrail.assert_called_once_with('cover')
        self.assertEqual(post.call_args.args[1]['quality'], 'low')

    @patch.object(proxy, 'ask_gms')
    def test_text_recommendation(self, ask):
        ask.side_effect = ['{"is_appropriate": true}', 'result']
        self.assertEqual(proxy.chat_completions(ChatRequest(messages=[{'role': 'user', 'content': 'novel'}])), {'content': 'result'})
        self.assertEqual(ask.call_args.args[1], 'gpt-5-nano')
