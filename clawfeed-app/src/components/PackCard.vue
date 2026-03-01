<template>
  <view class="pack-card" @click="$emit('click')">
    <view class="pack-header">
      <view class="pack-icon-wrap">
        <text class="pack-icon">📦</text>
      </view>
      <view class="pack-info">
        <text class="pack-name">{{ pack.name }}</text>
        <view class="pack-meta">
          <text class="pack-count">{{ (pack.sources || []).length }} 个源</text>
          <text class="pack-dot">·</text>
          <text class="pack-installs">{{ pack.install_count || 0 }} 次安装</text>
        </view>
      </view>
    </view>
    <text class="pack-desc">{{ pack.description || "暂无描述" }}</text>
    <view class="pack-footer">
      <text class="pack-creator">by {{ pack.creator_name || "匿名" }}</text>
      <view class="pack-arrow">
        <text class="arrow-text">→</text>
      </view>
    </view>
  </view>
</template>

<script setup>
defineProps({
  pack: { type: Object, required: true },
});
defineEmits(["click"]);
</script>

<style lang="scss" scoped>
.pack-card {
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  transition: all 0.25s ease;
}

.pack-card:active {
  transform: scale(0.98);
  border-color: #00d4ff;
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.2);
}

.pack-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.pack-icon-wrap {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(168, 85, 247, 0.15));
  border-radius: 16rpx;
}

.pack-icon {
  font-size: 36rpx;
}

.pack-info {
  flex: 1;
}

.pack-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #e8e8f0;
  margin-bottom: 6rpx;
}

.pack-meta {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.pack-count {
  font-size: 22rpx;
  color: #00d4ff;
}

.pack-dot {
  font-size: 22rpx;
  color: #5a5a70;
}

.pack-installs {
  font-size: 22rpx;
  color: #5a5a70;
}

.pack-desc {
  display: block;
  font-size: 26rpx;
  color: #8888a0;
  line-height: 1.6;
  margin-bottom: 16rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pack-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pack-creator {
  font-size: 22rpx;
  color: #5a5a70;
}

.pack-arrow {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 50%;
  transition: all 0.25s ease;
}

.pack-card:active .pack-arrow {
  background: rgba(0, 212, 255, 0.2);
}

.arrow-text {
  font-size: 24rpx;
  color: #00d4ff;
}
</style>