<template>
  <view class="container">
    <!-- Add source -->
    <view class="add-section">
      <input
        v-model="newUrl"
        class="url-input"
        placeholder="粘贴 URL 添加信息源..."
        confirm-type="done"
        @confirm="resolveUrl"
      />
      <button class="btn-add" size="mini" :loading="resolving" @click="resolveUrl">
        识别
      </button>
    </view>

    <!-- Resolve preview -->
    <view v-if="resolved" class="resolved-card">
      <view class="resolved-header">
        <text class="resolved-icon">{{ resolved.icon }}</text>
        <text class="resolved-name">{{ resolved.name }}</text>
        <text class="resolved-type">{{ resolved.type }}</text>
      </view>
      <view v-if="resolved.preview" class="resolved-preview">
        <text v-for="(p, i) in resolved.preview" :key="i" class="preview-item">
          {{ p.title }}
        </text>
      </view>
      <button class="btn-confirm" size="mini" @click="addSource">添加信息源</button>
    </view>

    <!-- Source list -->
    <view class="section-title">我的信息源</view>
    <view v-if="loading" class="loading">加载中...</view>
    <view v-for="source in sources" :key="source.id" class="source-card">
      <view class="source-info">
        <text class="source-name">{{ source.name }}</text>
        <text class="source-type">{{ source.type }}</text>
      </view>
      <view class="source-actions">
        <text
          v-if="source.subscribed"
          class="btn-unsub"
          @click="toggleSub(source)"
        >
          已订阅
        </text>
        <text v-else class="btn-sub" @click="toggleSub(source)">订阅</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";

const api = useApi();
const sources = ref([]);
const loading = ref(true);
const newUrl = ref("");
const resolving = ref(false);
const resolved = ref(null);

async function fetchSources() {
  loading.value = true;
  try {
    sources.value = await api.getSources();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function resolveUrl() {
  const url = newUrl.value.trim();
  if (!url) return;
  resolving.value = true;
  resolved.value = null;
  try {
    resolved.value = await api.resolveSource(url);
  } catch (e) {
    uni.showToast({ title: "无法识别该 URL", icon: "none" });
  } finally {
    resolving.value = false;
  }
}

async function addSource() {
  if (!resolved.value) return;
  try {
    await api.createSource({
      name: resolved.value.name,
      type: resolved.value.type,
      config: JSON.stringify(resolved.value.config),
    });
    uni.showToast({ title: "添加成功", icon: "success" });
    resolved.value = null;
    newUrl.value = "";
    fetchSources();
  } catch (e) {
    uni.showToast({ title: "添加失败", icon: "none" });
  }
}

async function toggleSub(source) {
  try {
    if (source.subscribed) {
      await api.unsubscribe(source.id);
      source.subscribed = false;
    } else {
      await api.subscribe(source.id);
      source.subscribed = true;
    }
  } catch (e) {
    uni.showToast({ title: "操作失败", icon: "none" });
  }
}

onShow(() => fetchSources());
onMounted(() => fetchSources());
</script>

<style scoped>
.container {
  padding: 24rpx;
}
.add-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.url-input {
  flex: 1;
  height: 72rpx;
  padding: 0 20rpx;
  background: #fff;
  border-radius: 12rpx;
  font-size: 26rpx;
  border: 1px solid #e8e8e8;
}
.btn-add {
  background: #1890ff;
  color: #fff;
  border: none;
  height: 72rpx;
  line-height: 72rpx;
}
.resolved-card {
  background: #fff;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
}
.resolved-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}
.resolved-icon {
  font-size: 36rpx;
}
.resolved-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}
.resolved-type {
  font-size: 22rpx;
  color: #999;
  background: #f0f0f0;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}
.preview-item {
  display: block;
  font-size: 24rpx;
  color: #666;
  padding: 4rpx 0;
}
.btn-confirm {
  margin-top: 16rpx;
  background: #52c41a;
  color: #fff;
  border: none;
}
.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 16rpx;
}
.source-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  margin-bottom: 12rpx;
  background: #fff;
  border-radius: 16rpx;
}
.source-info {
  flex: 1;
}
.source-name {
  font-size: 28rpx;
  color: #333;
  display: block;
  margin-bottom: 6rpx;
}
.source-type {
  font-size: 22rpx;
  color: #999;
}
.btn-sub {
  font-size: 24rpx;
  color: #1890ff;
  padding: 8rpx 20rpx;
  border: 1px solid #1890ff;
  border-radius: 8rpx;
}
.btn-unsub {
  font-size: 24rpx;
  color: #999;
  padding: 8rpx 20rpx;
  border: 1px solid #ddd;
  border-radius: 8rpx;
}
.loading {
  text-align: center;
  padding: 40rpx;
  color: #999;
}
</style>
