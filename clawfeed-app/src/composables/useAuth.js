/**
 * Auth composable — handles WeChat login and token management.
 */

import { useUserStore } from "../store/user";
import { useApi } from "./useApi";

export function useAuth() {
  const api = useApi();
  const userStore = useUserStore();

  /**
   * WeChat Mini-Program login flow:
   * 1. wx.login() → get code
   * 2. POST /api/auth/login { code } → get JWT + user info
   * 3. Store token & user locally
   */
  async function wxLogin() {
    return new Promise((resolve, reject) => {
      uni.login({
        provider: "weixin",
        success: async (loginRes) => {
          try {
            const result = await api.login({
              code: loginRes.code,
            });
            if (result.token) {
              uni.setStorageSync("token", result.token);
              uni.setStorageSync("user", JSON.stringify(result.user));
              userStore.setUser(result.user);
              resolve(result.user);
            } else {
              reject(new Error(result.error || "login failed"));
            }
          } catch (e) {
            reject(e);
          }
        },
        fail: reject,
      });
    });
  }

  /**
   * Dev login — for H5 debugging without WeChat.
   */
  async function devLogin() {
    const result = await api.devLogin();
    if (result.token) {
      uni.setStorageSync("token", result.token);
      uni.setStorageSync("user", JSON.stringify(result.user));
      userStore.setUser(result.user);
    }
    return result;
  }

  function logout() {
    uni.removeStorageSync("token");
    uni.removeStorageSync("user");
    userStore.clearUser();
  }

  function isLoggedIn() {
    return !!uni.getStorageSync("token");
  }

  return { wxLogin, devLogin, logout, isLoggedIn };
}
