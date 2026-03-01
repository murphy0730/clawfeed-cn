<template>
  <view class="loading-container" :class="{ 'loading-fullscreen': fullscreen }">
    <view class="loading-spinner" :style="{ width: size + 'rpx', height: size + 'rpx' }">
      <view class="spinner-ring"></view>
      <view class="spinner-ring"></view>
      <view class="spinner-ring"></view>
    </view>
    <text v-if="text" class="loading-text">{{ text }}</text>
  </view>
</template>

<script setup>
defineProps({
  text: {
    type: String,
    default: ""
  },
  size: {
    type: [Number, String],
    default: 64
  },
  fullscreen: {
    type: Boolean,
    default: false
  }
});
</script>

<style lang="scss" scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48rpx;
}

.loading-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 10, 15, 0.9);
  z-index: 999;
}

.loading-spinner {
  position: relative;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
}

.spinner-ring:nth-child(1) {
  border-top-color: #00d4ff;
  animation: spin 1s linear infinite;
}

.spinner-ring:nth-child(2) {
  border-right-color: #a855f7;
  animation: spin 1.5s linear infinite reverse;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #ec4899;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  margin-top: 24rpx;
  font-size: 26rpx;
  color: #8888a0;
  text-align: center;
}
</style>