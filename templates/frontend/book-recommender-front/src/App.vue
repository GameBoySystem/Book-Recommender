<!-- File: src/components/Recommender.vue -->
<template>
aaaaaa
 <el-form>
  <el-form-item>
    <el-select/>
  </el-form>
  <el-form-item>
    <el-select/>
  </el-form>
 
 </el-form>
</template>

<script>
import { ref, onMounted } from 'vue';
import {
  ElContainer,
  ElHeader,
  ElMain,
  ElForm,
  ElFormItem,
  ElInput,
  ElSelect,
  ElOption,
  ElButton,
  ElCard
} from 'element-plus';

export default {
  name: 'Recommender',
  components: {
    ElContainer,
    ElHeader,
    ElMain,
    ElForm,
    ElFormItem,
    ElInput,
    ElSelect,
    ElOption,
    ElButton,
    ElCard
  },
  setup() {
    const form = ref({
      searchQuery: '',
      selectedOptions: []
    });
    const searchResults = ref([]);
    const selectedBooks = ref([]);
    const recommendations = ref([]);
    const posters = ref([]);
    const authors = ref([]);
    const selectVisible = ref(false);
    const theme = ref('light');

    const toggleSelectVisibility = () => {
      selectVisible.value = true;
    };

    const searchBooks = async () => {
      if (form.value.searchQuery) {
        const response = await fetch(`/api/search?query=${encodeURIComponent(form.value.searchQuery)}`);
        const data = await response.json();
        searchResults.value = data;
      }
    };

    const addSelectedBook = (bookName) => {
      if (!selectedBooks.value.includes(bookName)) {
        selectedBooks.value.push(bookName);
      }
    };

    const addSelectedBooks = () => {
      form.value.selectedOptions.forEach((book) => {
        addSelectedBook(book);
      });
    };

    const removeBook = (bookName) => {
      selectedBooks.value = selectedBooks.value.filter((book) => book !== bookName);
    };

    const getRecommendations = async () => {
      const response = await fetch('/api/recommend/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ selected_books: selectedBooks.value })
      });
      if (response.ok) {
        const data = await response.json();
        recommendations.value = data.recommended_books;
        posters.value = data.poster_url;
        authors.value = data.authors;
      } else {
        alert('Ошибка при получении рекомендаций');
      }
    };

    const loadBooks = async () => {
      const response = await fetch('/api/books');
      const data = await response.json();
      searchResults.value = data;
    };

    const toggleTheme = () => {
      theme.value = theme.value === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', theme.value);
    };

    onMounted(loadBooks);

    return {
      form,
      searchResults,
      selectedBooks,
      recommendations,
      posters,
      authors,
      selectVisible,
      theme,
      toggleSelectVisibility,
      searchBooks,
      addSelectedBook,
      addSelectedBooks,
      removeBook,
      getRecommendations,
      toggleTheme,
    };
  }
};
</script>

<style scoped>
:root {
  --background-light: #f0f0f0;
  --background-dark: #333;
  --text-light: #333;
  --text-dark: #f0f0f0;
}

[data-theme='light'] {
  background-color: var(--background-light);
  color: var(--text-light);
}

[data-theme='dark'] {
  background-color: var(--background-dark);
  color: var(--text-dark);
}

.book-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}

.book {
  padding: 10px;
  width: 150px;
  text-align: center;
}

.book img {
  width: 100%;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.book .author {
  font-size: 14px;
  color: #777;
}

.selected-book {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
</style>
