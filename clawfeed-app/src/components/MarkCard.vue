<template>
  <view class="mark-card">
    <view class="info">
      <text class="title">{{ mark.title || mark.url }}</text>
      <text class="time">{{ timeAgo(mark.created_at) }}</text>
    </view>
    <slot name="action" />
  </view>
</template>

<script setup>
import { timeAgo } from "../utils/format";

defineProps({
  mark: { type: Object, required: true },
});
</script>

<style scoped>
.mark-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  margin-bottom: 12rpx;
  background: #fff;
  border-radius: 16rpx;
}
.info {
  flex: 1;
}
.title {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}
.time {
  font-size: 22rpx;
  color: #999;
}
</style>
