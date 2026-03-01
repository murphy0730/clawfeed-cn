<template>
  <view class="empty-container">
    <view class="empty-icon">
      <text class="icon-text">{{ icon }}</text>
    </view>
    <text class="empty-title">{{ title }}</text>
    <text v-if="description" class="empty-description">{{ description }}</text>
    <view v-if="actionText" class="empty-action" @click="$emit('action')">
      <text class="action-text">{{ actionText }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: "📭"
  },
  title: {
    type: String,
    default: "暂无内容"
  },
  description: {
    type: String,
    default: ""
  },
  actionText: {
    type: String,
    default: ""
  }
});

defineEmits(["action"]);
</script>

<style lang="scss" scoped>
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 32rpx;
}

.empty-icon {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(168, 85, 247, 0.1));
  border: 1px solid rgba(0, 212, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.icon-text {
  font-size: 64rpx;
  opacity: 0.8;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #e8e8f0;
  margin-bottom: 12rpx;
  text-align: center;
}

.empty-description {
  font-size: 26rpx;
  color: #8888a0;
  text-align: center;
  max-width: 480rpx;
  line-height: 1.6;
  margin-bottom: 32rpx;
}

.empty-action {
  padding: 20rpx 48rpx;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 16rpx;
  transition: all 0.25s ease;
}

.empty-action:active {
  transform: scale(0.96);
  opacity: 0.9;
}

.action-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
}
</style>