<template>
  <view class="digest-card" @click="$emit('click')">
    <view class="header">
      <text class="type">{{ digestTypeLabel(digest.type) }}</text>
      <text class="time">{{ timeAgo(digest.created_at) }}</text>
    </view>
    <text class="content">{{ truncate(digest.content, maxLength) }}</text>
  </view>
</template>

<script setup>
import { digestTypeLabel, timeAgo, truncate } from "../utils/format";

defineProps({
  digest: { type: Object, required: true },
  maxLength: { type: Number, default: 200 },
});
defineEmits(["click"]);
</script>

<style scoped>
.digest-card {
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}
.type {
  font-size: 24rpx;
  color: #1890ff;
  font-weight: 500;
}
.time {
  font-size: 22rpx;
  color: #999;
}
.content {
  font-size: 26rpx;
  color: #333;
  line-height: 1.6;
}
</style>
