<template>
  <div class="login-container">
    <div class="login-header">
      W.F.M TRAINER
    </div>
    <form class="login-form" @submit.prevent="login">
      <h2>Login</h2>
      <input type="text" placeholder="Login" v-model="username"/>
      <input type="password" placeholder="Password" v-model="password"/>
      <button class="login-button">Connexion</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:8000/login/', {
          username: this.username,
          password: this.password
        });
        localStorage.setItem('jwt', response.data.access);
        localStorage.setItem('jwt_refresh', response.data.refresh);
        this.$router.replace({ name: 'Home' });
      } catch (error) {
        console.error(error);
        alert("Échec de la connexion. Veuillez vérifier vos identifiants.");
      }
    }
  }
};
</script>

<style>
  .login-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;

  }

  .login-header {
    margin-bottom: 20px;
    font-size: 24px;
  }

  .login-form { 
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
    width: 300px;
  }

  .login-form h2 {
    text-align: center;
    margin-bottom: 20px;
  }

  .login-form input {
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
  }

  .login-button {
    width: 100%;
    padding: 10px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }

  .login-button:hover {
    background: #0056b3;
  }
</style>