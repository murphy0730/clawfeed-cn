<template>
  <view class="container">
    <view v-if="loading" class="loading">加载中...</view>
    <view v-else-if="pack" class="detail">
      <view class="header">
        <text class="name">{{ pack.name }}</text>
        <text class="creator">by {{ pack.creator_name || "匿名" }}</text>
      </view>
      <text class="desc">{{ pack.description || "暂无描述" }}</text>

      <view class="section-title">包含的信息源 ({{ (pack.sources || []).length }})</view>
      <view v-for="(s, i) in pack.sources || []" :key="i" class="source-item">
        <text class="source-icon">{{ s.icon || "📡" }}</text>
        <view class="source-info">
          <text class="source-name">{{ s.name }}</text>
          <text class="source-type">{{ s.type }}</text>
        </view>
      </view>

      <button class="btn-install" :loading="installing" @click="install">
        一键安装
      </button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";

const api = useApi();
const pack = ref(null);
const loading = ref(true);
const installing = ref(false);
let slug = null;

onLoad((query) => {
  slug = query.slug;
});

onMounted(async () => {
  if (!slug) return;
  try {
    pack.value = await api.getPack(slug);
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
});

async function install() {
  if (!slug) return;
  installing.value = true;
  try {
    const result = await api.installPack(slug);
    uni.showToast({
      title: `安装成功，添加了 ${result.added} 个信息源`,
      icon: "none",
    });
  } catch (e) {
    uni.showToast({ title: "安装失败", icon: "none" });
  } finally {
    installing.value = false;
  }
}
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.header {
  margin-bottom: 16rpx;
}
.name {
  font-size: 36rpx;
  font-weight: 700;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
}
.creator {
  font-size: 24rpx;
  color: #999;
}
.desc {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 32rpx;
  display: block;
}
.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}
.source-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 24rpx;
  margin-bottom: 8rpx;
  background: #fff;
  border-radius: 12rpx;
}
.source-icon {
  font-size: 36rpx;
}
.source-name {
  font-size: 28rpx;
  color: #333;
  display: block;
}
.source-type {
  font-size: 22rpx;
  color: #999;
}
.btn-install {
  margin-top: 40rpx;
  background: #1890ff;
  color: #fff;
  border: none;
  border-radius: 12rpx;
}
.loading {
  text-align: center;
  padding: 60rpx;
  color: #999;
}
</style>
