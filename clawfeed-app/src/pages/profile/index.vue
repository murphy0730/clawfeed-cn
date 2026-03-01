<template>
  <view class="page-container">
    <!-- User section -->
    <view v-if="userStore.isLoggedIn" class="user-section">
      <view class="user-card">
        <view class="user-bg"></view>
        <view class="user-content">
          <view class="avatar-wrapper">
            <image
              v-if="userStore.user?.avatar"
              class="avatar"
              :src="userStore.user.avatar"
              mode="aspectFill"
            />
            <view v-else class="avatar-placeholder">
              <text class="avatar-text">{{ (userStore.user?.name || "U")[0] }}</text>
            </view>
          </view>
          <view class="user-info">
            <text class="user-name">{{ userStore.user?.name || "用户" }}</text>
            <text class="user-slug">@{{ userStore.user?.slug || "user" }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Login section -->
    <view v-else class="login-section">
      <view class="login-card">
        <view class="login-icon">
          <text class="icon-text">⚡</text>
        </view>
        <text class="login-title">欢迎来到 ClawFeed</text>
        <text class="login-desc">登录后可以订阅信息源、收藏摘要</text>
        <!-- #ifdef MP-WEIXIN -->
        <view class="login-btn" @click="handleWxLogin">
          <text class="login-btn-text">微信登录</text>
        </view>
        <!-- #endif -->
        <!-- #ifdef H5 -->
        <view class="login-btn" @click="handleDevLogin">
          <text class="login-btn-text">开发者登录</text>
        </view>
        <!-- #endif -->
      </view>
    </view>

    <!-- Menu section -->
    <view class="menu-section">
      <view class="menu-card">
        <view class="menu-item" @click="goTo('/pages/packs/index')">
          <view class="menu-icon-wrap">
            <text class="menu-icon">📦</text>
          </view>
          <text class="menu-label">Pack 市场</text>
          <text class="menu-arrow">→</text>
        </view>
        <view class="menu-divider"></view>
        <view class="menu-item" @click="goTo('/pages/feedback/index')">
          <view class="menu-icon-wrap">
            <text class="menu-icon">💬</text>
          </view>
          <text class="menu-label">反馈建议</text>
          <text class="menu-arrow">→</text>
        </view>
      </view>
    </view>

    <!-- Logout section -->
    <view v-if="userStore.isLoggedIn" class="logout-section">
      <view class="logout-btn" @click="handleLogout">
        <text class="logout-text">退出登录</text>
      </view>
    </view>

    <!-- Version info -->
    <view class="version-section">
      <text class="version-text">ClawFeed v1.0.0</text>
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

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
  padding: 24rpx;
}

.user-section {
  margin-bottom: 24rpx;
}

.user-card {
  position: relative;
  border-radius: 24rpx;
  overflow: hidden;
}

.user-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(168, 85, 247, 0.15));
}

.user-content {
  position: relative;
  display: flex;
  align-items: center;
  padding: 32rpx 24rpx;
}

.avatar-wrapper {
  margin-right: 24rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  border: 3px solid rgba(0, 212, 255, 0.3);
}

.avatar-placeholder {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 40rpx;
  font-weight: 700;
  color: #ffffff;
}

.user-info {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 34rpx;
  font-weight: 600;
  color: #e8e8f0;
  margin-bottom: 6rpx;
}

.user-slug {
  font-size: 24rpx;
  color: #8888a0;
}

.login-section {
  margin-bottom: 24rpx;
}

.login-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 24rpx;
}

.login-icon {
  width: 100rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(168, 85, 247, 0.15));
  border-radius: 24rpx;
  margin-bottom: 24rpx;
}

.icon-text {
  font-size: 48rpx;
}

.login-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #e8e8f0;
  margin-bottom: 8rpx;
}

.login-desc {
  font-size: 26rpx;
  color: #8888a0;
  margin-bottom: 32rpx;
  text-align: center;
}

.login-btn {
  padding: 24rpx 80rpx;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 16rpx;
  transition: all 0.25s ease;
}

.login-btn:active {
  transform: scale(0.96);
  opacity: 0.9;
}

.login-btn-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #ffffff;
}

.menu-section {
  margin-bottom: 24rpx;
}

.menu-card {
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 24rpx;
  transition: all 0.25s ease;
}

.menu-item:active {
  background: rgba(0, 212, 255, 0.05);
}

.menu-icon-wrap {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12rpx;
  margin-right: 16rpx;
}

.menu-icon {
  font-size: 24rpx;
}

.menu-label {
  flex: 1;
  font-size: 30rpx;
  color: #e8e8f0;
}

.menu-arrow {
  font-size: 28rpx;
  color: #5a5a70;
}

.menu-divider {
  height: 1px;
  background: #2a2a3a;
  margin: 0 24rpx;
}

.logout-section {
  margin-bottom: 24rpx;
}

.logout-btn {
  padding: 28rpx 0;
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 16rpx;
  text-align: center;
  transition: all 0.25s ease;
}

.logout-btn:active {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.logout-text {
  font-size: 30rpx;
  color: #ef4444;
}

.version-section {
  text-align: center;
  padding: 24rpx 0;
}

.version-text {
  font-size: 22rpx;
  color: #3a3a4a;
}
</style>