<template>
  <view class="source-card" @click="$emit('click')">
    <view class="source-content">
      <view class="source-icon-wrap">
        <text class="source-icon">{{ getSourceIcon(source.type) }}</text>
      </view>
      <view class="source-info">
        <text class="source-name">{{ source.name }}</text>
        <text class="source-type">{{ source.type }}</text>
      </view>
    </view>
    <slot name="action" />
  </view>
</template>

<script setup>
defineProps({
  source: { type: Object, required: true },
});
defineEmits(["click"]);

function getSourceIcon(type) {
  const icons = {
    twitter: "🐦",
    rss: "📡",
    hackernews: "🔶",
    reddit: "🔴",
    github: "🐙",
  };
  return icons[type] || "📡";
}
</script>

<style lang="scss" scoped>
.source-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 16rpx;
  margin-bottom: 12rpx;
  transition: all 0.25s ease;
}

.source-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
}

.source-content {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
  min-width: 0;
}

.source-icon-wrap {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12rpx;
}

.source-icon {
  font-size: 32rpx;
}

.source-info {
  flex: 1;
  min-width: 0;
}

.source-name {
  display: block;
  font-size: 28rpx;
  color: #e8e8f0;
  font-weight: 500;
  margin-bottom: 4rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-type {
  display: block;
  font-size: 22rpx;
  color: #5a5a70;
}
</style>