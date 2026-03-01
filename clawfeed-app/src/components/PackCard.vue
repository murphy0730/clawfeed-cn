<template>
  <view class="pack-card" @click="$emit('click')">
    <view class="header">
      <text class="name">{{ pack.name }}</text>
      <text class="count">{{ (pack.sources || []).length }} 个信息源</text>
    </view>
    <text class="desc">{{ pack.description || "暂无描述" }}</text>
    <view class="footer">
      <text class="installs">{{ pack.install_count || 0 }} 次安装</text>
      <text class="creator">by {{ pack.creator_name || "匿名" }}</text>
    </view>
  </view>
</template>

<script setup>
defineProps({
  pack: { type: Object, required: true },
});
defineEmits(["click"]);
</script>

<style scoped>
.pack-card {
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: #fff;
  border-radius: 16rpx;
}
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8rpx;
}
.name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}
.count {
  font-size: 22rpx;
  color: #1890ff;
}
.desc {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}
.footer {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #999;
}
</style>
