import { defineStore } from "pinia";
import { ref } from "vue";

export const useUserStore = defineStore("user", () => {
  const user = ref(null);
  const isLoggedIn = ref(false);

  function setUser(u) {
    user.value = u;
    isLoggedIn.value = true;
  }

  function clearUser() {
    user.value = null;
    isLoggedIn.value = false;
  }

  function checkLogin() {
    const token = uni.getStorageSync("token");
    const saved = uni.getStorageSync("user");
    if (token && saved) {
      try {
        user.value = JSON.parse(saved);
        isLoggedIn.value = true;
      } catch {
        clearUser();
      }
    }
  }

  return { user, isLoggedIn, setUser, clearUser, checkLogin };
});
