<template>
    <nav>
        <h1 @click="refreshPage">WFM API</h1>
        <button class="btn-logout" @click="logout">
            logout
        </button>
    </nav>
</template>

<script>

export default {
    methods: {
        logout() {
        localStorage.removeItem('jwt');
        this.$router.push({ name: 'Login' }); 
        },
        refreshPage() {
            window.location.reload();
        }
    }
};
</script>
  
<style>
    nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background-color: #0584a1;
        color: #fff; 
    }

    h1 {
        margin: 0; 
        font-size: 1.5rem;
        cursor: pointer;
    }

    .btn-logout {
        padding: 10px 20px;
        background-color: #0584a112;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 1rem;
        border-radius: 5px;
        transition: all 0.5s ease;
        box-shadow: inset 0 4px 8px rgba(255, 255, 255, 0.3),
                    inset 4px 0 12px rgba(0, 0, 0, 0.3),
                    0px 0px 3px rgba(0, 0, 0, 0.2);
      }
        
      .btn-logout img {
        color: #fff
      }
    
      .btn-logout:hover {
        background-color: #1645649b;
      }
      
      .btn-logout:active {
        box-shadow: inset 4px 9px 12px rgba(0, 0, 0, 0.3);
        transform: translateY(2px);
      }
      
</style>
