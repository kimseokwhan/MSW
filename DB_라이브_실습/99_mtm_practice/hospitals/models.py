from django.db import models


# class Doctor(models.Model):
#     name = models.TextField()

#     def __str__(self):
#         return f'{self.pk}번 의사 {self.name}'


# class Patient(models.Model):
#     # 외래키 하나론 어렵다
#     # doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     name = models.TextField()

#     def __str__(self):
#         return f'{self.pk}번 환자 {self.name}'


# 둘을 이어주는 매개 (중계) 테이블
# class Reservation(models.Model):
#     doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
#     def __str__(self):
#         return f'{self.doctor_id}: {self.patient_id}'


# class Doctor(models.Model):
#     name = models.TextField()

#     def __str__(self):
#         return f'{self.pk}번 의사 {self.name}'


# class Patient(models.Model):
#     # ManyToManyField 작성
#     doctors = models.ManyToManyField(Doctor)
#     name = models.TextField()

#     def __str__(self):
#         return f'{self.pk}번 환자 {self.name}'

class Doctor(models.Model):
    name = models.TextField()

    def __str__(self):
        return f'{self.pk}번 의사 {self.name}'


class Patient(models.Model):
    doctors = models.ManyToManyField(Doctor, through='Reservation')
    name = models.TextField()

    def __str__(self):
        return f'{self.pk}번 환자 {self.name}'


class Reservation(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.TextField()
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.doctor.pk}번 의사의 {self.patient.pk}번 환자'