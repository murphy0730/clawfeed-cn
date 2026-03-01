<template>
  <view class="digest-card" @click="$emit('click')">
    <view class="card-header">
      <view class="type-badge" :class="getTypeClass(digest.type)">
        <text class="type-text">{{ digestTypeLabel(digest.type) }}</text>
      </view>
      <text class="time-text">{{ timeAgo(digest.created_at) }}</text>
    </view>
    <view class="card-content">
      <text class="content-text">{{ truncate(digest.content, maxLength) }}</text>
    </view>
    <view class="card-footer">
      <view class="footer-line"></view>
    </view>
  </view>
</template>

<script setup>
import { digestTypeLabel, timeAgo, truncate } from "../utils/format";

defineProps({
  digest: { type: Object, required: true },
  maxLength: { type: Number, default: 200 },
});
defineEmits(["click"]);

function getTypeClass(type) {
  const classes = {
    "4h": "cyan",
    daily: "purple",
    weekly: "green",
    monthly: "orange",
  };
  return classes[type] || "cyan";
}
</script>

<style lang="scss" scoped>
.digest-card {
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  transition: all 0.25s ease;
}

.digest-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.type-badge {
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  background: rgba(0, 212, 255, 0.12);
}

.type-badge.cyan {
  background: rgba(0, 212, 255, 0.12);
}

.type-badge.purple {
  background: rgba(168, 85, 247, 0.12);
}

.type-badge.green {
  background: rgba(34, 197, 94, 0.12);
}

.type-badge.orange {
  background: rgba(245, 158, 11, 0.12);
}

.type-text {
  font-size: 22rpx;
  font-weight: 600;
  color: #00d4ff;
}

.type-badge.purple .type-text {
  color: #a855f7;
}

.type-badge.green .type-text {
  color: #22c55e;
}

.type-badge.orange .type-text {
  color: #f59e0b;
}

.time-text {
  font-size: 22rpx;
  color: #5a5a70;
}

.card-content {
  margin-bottom: 16rpx;
}

.content-text {
  font-size: 28rpx;
  color: #e8e8f0;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: center;
}

.footer-line {
  width: 48rpx;
  height: 4rpx;
  background: linear-gradient(90deg, #00d4ff, #a855f7);
  border-radius: 2rpx;
  opacity: 0.3;
}
</style>