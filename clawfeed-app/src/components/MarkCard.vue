<template>
  <view class="mark-card" @click="$emit('click')">
    <view class="card-content">
      <text class="mark-title">{{ mark.title || mark.url }}</text>
      <text class="mark-time">{{ timeAgo(mark.created_at) }}</text>
    </view>
    <slot name="action" />
  </view>
</template>

<script setup>
import { timeAgo } from "../utils/format";

defineProps({
  mark: { type: Object, required: true },
});
defineEmits(["click"]);
</script>

<style lang="scss" scoped>
.mark-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  transition: all 0.25s ease;
}

.mark-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
}

.card-content {
  flex: 1;
  min-width: 0;
}

.mark-title {
  display: block;
  font-size: 28rpx;
  color: #e8e8f0;
  font-weight: 500;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mark-time {
  display: block;
  font-size: 22rpx;
  color: #5a5a70;
}
</style>