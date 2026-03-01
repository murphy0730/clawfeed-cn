<template>
  <view class="container">
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else>
      <view v-if="!packs.length" class="empty">暂无 Pack</view>
      <view v-for="pack in packs" :key="pack.id" class="pack-card" @click="goDetail(pack.slug)">
        <view class="pack-header">
          <text class="pack-name">{{ pack.name }}</text>
          <text class="pack-count">{{ (pack.sources || []).length }} 个信息源</text>
        </view>
        <text class="pack-desc">{{ pack.description || "暂无描述" }}</text>
        <view class="pack-footer">
          <text class="pack-installs">{{ pack.install_count || 0 }} 次安装</text>
          <text class="pack-creator">by {{ pack.creator_name || "匿名" }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";

const api = useApi();
const packs = ref([]);
const loading = ref(true);

async function fetchPacks() {
  loading.value = true;
  try {
    packs.value = await api.getPacks();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

function goDetail(slug) {
  uni.navigateTo({ url: `/pages/packs/detail?slug=${slug}` });
}

onShow(() => fetchPacks());
onMounted(() => fetchPacks());
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.pack-card {
  padding: 24rpx;
  margin-bottom: 16rpx;
  background: #fff;
  border-radius: 16rpx;
}
.pack-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8rpx;
}
.pack-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}
.pack-count {
  font-size: 22rpx;
  color: #1890ff;
}
.pack-desc {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}
.pack-footer {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #999;
}
.loading,
.empty {
  text-align: center;
  padding: 60rpx;
  color: #999;
}
</style>
