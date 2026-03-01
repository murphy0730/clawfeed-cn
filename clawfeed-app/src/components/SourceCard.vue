<template>
  <view class="source-card">
    <view class="info">
      <text class="name">{{ source.name }}</text>
      <text class="type">{{ source.type }}</text>
    </view>
    <slot name="action" />
  </view>
</template>

<script setup>
defineProps({
  source: { type: Object, required: true },
});
</script>

<style scoped>
.source-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  margin-bottom: 12rpx;
  background: #fff;
  border-radius: 16rpx;
}
.name {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}
.type {
  font-size: 22rpx;
  color: #999;
}
</style>
