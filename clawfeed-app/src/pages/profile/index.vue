<template>
  <view class="container">
    <!-- User info -->
    <view class="user-section" v-if="userStore.isLoggedIn">
      <image
        v-if="userStore.user?.avatar"
        class="avatar"
        :src="userStore.user.avatar"
        mode="aspectFill"
      />
      <view v-else class="avatar-placeholder">{{ (userStore.user?.name || "U")[0] }}</view>
      <view class="user-info">
        <text class="user-name">{{ userStore.user?.name || "用户" }}</text>
        <text class="user-slug">{{ userStore.user?.slug || "" }}</text>
      </view>
    </view>
    <view v-else class="login-section">
      <!-- #ifdef MP-WEIXIN -->
      <button class="btn-login" @click="handleWxLogin">微信登录</button>
      <!-- #endif -->
      <!-- #ifdef H5 -->
      <button class="btn-login" @click="handleDevLogin">开发者登录</button>
      <!-- #endif -->
    </view>

    <!-- Menu items -->
    <view class="menu-section">
      <view class="menu-item" @click="goTo('/pages/packs/index')">
        <text class="menu-label">Pack 市场</text>
        <text class="menu-arrow">></text>
      </view>
      <view class="menu-item" @click="goTo('/pages/feedback/index')">
        <text class="menu-label">反馈建议</text>
        <text class="menu-arrow">></text>
      </view>
    </view>

    <!-- Logout -->
    <view v-if="userStore.isLoggedIn" class="logout-section">
      <button class="btn-logout" @click="handleLogout">退出登录</button>
    </view>
  </view>
</template>

<script setup>
import { useUserStore } from "../../store/user";
import { useAuth } from "../../composables/useAuth";

const userStore = useUserStore();
const auth = useAuth();

async function handleWxLogin() {
  try {
    await auth.wxLogin();
    uni.showToast({ title: "登录成功", icon: "success" });
  } catch (e) {
    uni.showToast({ title: "登录失败", icon: "none" });
  }
}

async function handleDevLogin() {
  try {
    await auth.devLogin();
    uni.showToast({ title: "登录成功", icon: "success" });
  } catch (e) {
    uni.showToast({ title: "登录失败", icon: "none" });
  }
}

function handleLogout() {
  uni.showModal({
    title: "确认退出",
    content: "确定要退出登录吗？",
    success(res) {
      if (res.confirm) {
        auth.logout();
        uni.showToast({ title: "已退出", icon: "success" });
      }
    },
  });
}

function goTo(url) {
  uni.navigateTo({ url });
}
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.user-section {
  display: flex;
  align-items: center;
  padding: 32rpx 24rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
}
.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 24rpx;
}
.avatar-placeholder {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: #1890ff;
  color: #fff;
  font-size: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}
.user-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
}
.user-slug {
  font-size: 24rpx;
  color: #999;
}
.login-section {
  padding: 60rpx 24rpx;
  text-align: center;
}
.btn-login {
  background: #07c160;
  color: #fff;
  border: none;
  border-radius: 12rpx;
}
.menu-section {
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
}
.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 24rpx;
  border-bottom: 1px solid #f0f0f0;
}
.menu-item:last-child {
  border-bottom: none;
}
.menu-label {
  font-size: 28rpx;
  color: #333;
}
.menu-arrow {
  font-size: 28rpx;
  color: #ccc;
}
.logout-section {
  margin-top: 48rpx;
}
.btn-logout {
  background: #fff;
  color: #ff4d4f;
  border: 1px solid #ff4d4f;
  border-radius: 12rpx;
}
</style>
