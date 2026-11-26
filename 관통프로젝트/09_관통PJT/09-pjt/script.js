/**
 * 제공 코드
 */
// 기본 작가, 분류, 도서 데이터 (JavaScript Array)
const categories = categoryRawData
const authors = authorRawData
const books = bookRawData
// 데이터 확인
console.log(categories.length)
console.log(categories[0])
console.log(authors.length)
console.log(authors[0])
console.log(books.length)
console.log(books[0])

/**
 * 대부분의 작업은 script.js에서 진행해도 무방하나 원한다면 js 파일 추가 가능
 * HTML 요소 추가를 위한 `.innerHTML` 사용 금지, 요소의 내용을 비우는 용도로는 사용 가능 (`.innerHTML = ```)
 */

const favoriteBooks = new Set()
const bookListRow = document.querySelector('#book-list-row')
const favoritesListRow = document.querySelector('#favorites-list-row')
let homeBooks = books

function updateFavoriteButton(button, book) {
  const isFavorite = favoriteBooks.has(book)
  button.className = isFavorite ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary'
  button.textContent = isFavorite ? '즐겨찾기 취소' : '즐겨찾기 추가'
}

function renderBookList(bookList, row) {
  row.replaceChildren()

  for (const book of bookList) {
    const column = document.createElement('div')
    column.className = 'col-12 col-sm-6 col-md-4 col-lg-3'

    const card = document.createElement('article')
    card.className = 'card h-100'

    const cover = document.createElement('img')
    cover.className = 'card-img-top object-fit-contain'
    cover.style.aspectRatio = '1'
    cover.src = book.cover || 'stack-of-books.png'
    cover.alt = `${book.title} 표지`

    const body = document.createElement('div')
    body.className = 'card-body'

    const title = document.createElement('h3')
    title.className = 'card-title h5'
    title.textContent = book.title

    const description = document.createElement('p')
    description.className = 'card-text'
    description.textContent = book.description

    const favoriteButton = document.createElement('button')
    favoriteButton.type = 'button'
    updateFavoriteButton(favoriteButton, book)
    favoriteButton.addEventListener('click', () => {
      if (favoriteBooks.has(book)) {
        favoriteBooks.delete(book)
      } else {
        favoriteBooks.add(book)
      }

      if (row === favoritesListRow) {
        column.remove()
        if (favoriteBooks.size === 0) showTab('home')
      } else {
        updateFavoriteButton(favoriteButton, book)
      }
    })

    body.append(title, description, favoriteButton)
    card.append(cover, body)
    column.append(card)
    row.append(column)
  }
}

renderBookList(homeBooks, bookListRow)

function findBooks(field, keyword) {
  if (field === 'title') {
    return books.filter(book => book.title.includes(keyword))
  }

  const entries = field === 'authorId' ? authors : categories
  const matchingIds = new Set(entries
    .filter(entry => entry.name.includes(keyword))
    .map(entry => entry.id))
  return books.filter(book => matchingIds.has(book[field]))
}

const searchForm = document.querySelector('#search-form')
searchForm.addEventListener('submit', event => {
  event.preventDefault()
  const keyword = searchForm.elements.keyword.value.trim()
  if (!keyword) {
    alert('검색어를 입력하세요.')
    return
  }

  const field = searchForm.elements.field.value
  homeBooks = findBooks(field, keyword)
  renderBookList(homeBooks, bookListRow)
})

searchForm.addEventListener('reset', () => {
  homeBooks = books
  if (!homeContainer.classList.contains('d-none')) {
    renderBookList(homeBooks, bookListRow)
  }
})

const homeContainer = document.querySelector('#home-container')
const createContainer = document.querySelector('#create-container')
const favoritesContainer = document.querySelector('#favorites-container')
const favoritesEmpty = document.querySelector('#favorites-empty')

function showTab(tab) {
  homeContainer.classList.toggle('d-none', tab !== 'home')
  createContainer.classList.toggle('d-none', tab !== 'create')
  favoritesContainer.classList.toggle('d-none', tab !== 'favorites')

  if (tab === 'home') {
    renderBookList(homeBooks, bookListRow)
  } else if (tab === 'favorites') {
    favoritesEmpty.classList.toggle('d-none', favoriteBooks.size > 0)
    renderBookList(favoriteBooks, favoritesListRow)
  }
}

document.querySelector('#home-nav').addEventListener('click', () => showTab('home'))
document.querySelector('#create-nav').addEventListener('click', () => showTab('create'))
document.querySelector('#favorites-nav').addEventListener('click', () => showTab('favorites'))

function findOrCreateId(entries, name) {
  const existing = entries.find(entry => entry.name === name)
  if (existing) return existing.id

  const id = Math.max(0, ...entries.map(entry => entry.id)) + 1
  entries.push({ id, name })
  return id
}

const createForm = document.querySelector('#create-form')
const createErrors = document.querySelector('#create-book-errors')

createForm.addEventListener('submit', event => {
  event.preventDefault()
  const fields = createForm.elements
  const title = fields['title-input'].value.trim()
  const author = fields['author-input'].value.trim()
  const cover = fields['img-input'].value.trim()
  const description = fields['desc-input'].value.trim()
  const category = fields['category-input'].value.trim()

  createErrors.replaceChildren()
  const requiredFields = [
    [title, '제목을 입력하세요.'],
    [author, '작가를 입력하세요.'],
    [description, '소개를 입력하세요.'],
    [category, '분류를 입력하세요.'],
  ]
  for (const [value, message] of requiredFields) {
    if (!value) {
      const error = document.createElement('li')
      error.textContent = message
      createErrors.append(error)
    }
  }
  if (createErrors.childElementCount > 0) return

  books.unshift({
    title,
    description,
    cover: cover.startsWith('http') ? cover : '',
    authorId: findOrCreateId(authors, author),
    categoryId: findOrCreateId(categories, category),
  })
  createForm.reset()
  searchForm.reset()
  showTab('home')
})
