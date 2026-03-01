<template>
  <view class="page-container">
    <!-- Add source section -->
    <view class="add-section">
      <view class="input-wrapper">
        <input
          v-model="newUrl"
          class="url-input"
          placeholder="粘贴 URL 添加信息源..."
          placeholder-class="input-placeholder"
          confirm-type="done"
          @confirm="resolveUrl"
          @focus="inputFocused = true"
          @blur="inputFocused = false"
        />
      </view>
      <view
        class="resolve-btn"
        :class="{ loading: resolving }"
        @click="resolveUrl"
      >
        <text v-if="!resolving" class="btn-text">识别</text>
        <view v-else class="btn-spinner"></view>
      </view>
    </view>

    <!-- Resolve preview -->
    <view v-if="resolved" class="resolved-section">
      <view class="resolved-card neon-border-glow">
        <view class="resolved-header">
          <text class="resolved-icon">{{ resolved.icon || '📡' }}</text>
          <view class="resolved-info">
            <text class="resolved-name">{{ resolved.name }}</text>
            <view class="resolved-type-badge">
              <text class="resolved-type">{{ resolved.type }}</text>
            </view>
          </view>
        </view>
        <view v-if="resolved.preview && resolved.preview.length" class="resolved-preview">
          <text class="preview-label">预览内容：</text>
          <text
            v-for="(p, i) in resolved.preview.slice(0, 3)"
            :key="i"
            class="preview-item"
          >
            · {{ p.title }}
          </text>
        </view>
        <view class="resolved-actions">
          <view class="confirm-btn" @click="addSource">
            <text class="confirm-text">添加信息源</text>
          </view>
          <view class="cancel-btn" @click="resolved = null">
            <text class="cancel-text">取消</text>
          </view>
        </view>
      </view>
    </view>

    <!-- Source list section -->
    <view class="sources-section">
      <view class="section-header">
        <text class="section-title">我的信息源</text>
        <text class="section-count">{{ sources.length }} 个</text>
      </view>

      <!-- Loading -->
      <view v-if="loading" class="loading-wrapper">
        <XLoading text="加载中..." :size="48" />
      </view>

      <!-- Empty -->
      <XEmpty
        v-else-if="!sources.length"
        icon="📡"
        title="暂无信息源"
        description="在上方输入框粘贴 URL 添加信息源"
      />

      <!-- Source cards -->
      <view v-else class="sources-list">
        <view
          v-for="(source, index) in sources"
          :key="source.id"
          class="source-card"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="source-content">
            <view class="source-icon-wrap">
              <text class="source-icon">{{ getSourceIcon(source.type) }}</text>
            </view>
            <view class="source-info">
              <text class="source-name">{{ source.name }}</text>
              <text class="source-type">{{ source.type }}</text>
            </view>
          </view>
          <view class="source-actions">
            <view
              class="sub-btn"
              :class="{ subscribed: source.subscribed }"
              @click="toggleSub(source)"
            >
              <text class="sub-text">{{ source.subscribed ? '已订阅' : '订阅' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- Bottom padding -->
    <view class="bottom-padding"></view>
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onShow } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import XLoading from "../../components/XLoading.vue";
import XEmpty from "../../components/XEmpty.vue";

const api = useApi();
const sources = ref([]);
const loading = ref(true);
const newUrl = ref("");
const resolving = ref(false);
const resolved = ref(null);
const inputFocused = ref(false);

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

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
  padding: 24rpx;
}

.add-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.input-wrapper {
  flex: 1;
}

.url-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #e8e8f0;
  transition: all 0.25s ease;
}

.url-input:focus {
  border-color: #00d4ff;
  box-shadow: 0 0 20rpx rgba(0, 212, 255, 0.2);
}

.input-placeholder {
  color: #5a5a70;
}

.resolve-btn {
  width: 120rpx;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 16rpx;
  transition: all 0.25s ease;
}

.resolve-btn:active {
  transform: scale(0.96);
  opacity: 0.9;
}

.btn-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #ffffff;
}

.btn-spinner {
  width: 36rpx;
  height: 36rpx;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.resolved-section {
  margin-bottom: 24rpx;
}

.resolved-card {
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #00d4ff;
  border-radius: 20rpx;
  box-shadow: 0 0 24rpx rgba(0, 212, 255, 0.2);
}

.resolved-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.resolved-icon {
  font-size: 48rpx;
}

.resolved-info {
  flex: 1;
}

.resolved-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #e8e8f0;
  margin-bottom: 6rpx;
}

.resolved-type-badge {
  display: inline-block;
  padding: 4rpx 12rpx;
  background: rgba(0, 212, 255, 0.12);
  border-radius: 6rpx;
}

.resolved-type {
  font-size: 22rpx;
  color: #00d4ff;
}

.resolved-preview {
  padding: 16rpx;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12rpx;
  margin-bottom: 20rpx;
}

.preview-label {
  display: block;
  font-size: 22rpx;
  color: #8888a0;
  margin-bottom: 8rpx;
}

.preview-item {
  display: block;
  font-size: 24rpx;
  color: #8888a0;
  padding: 4rpx 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.resolved-actions {
  display: flex;
  gap: 16rpx;
}

.confirm-btn {
  flex: 1;
  padding: 16rpx 0;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 12rpx;
  text-align: center;
}

.confirm-btn:active {
  opacity: 0.9;
}

.confirm-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #ffffff;
}

.cancel-btn {
  padding: 16rpx 32rpx;
  background: transparent;
  border: 1px solid #2a2a3a;
  border-radius: 12rpx;
  transition: all 0.25s ease;
}

.cancel-btn:active {
  border-color: #8888a0;
}

.cancel-text {
  font-size: 26rpx;
  color: #8888a0;
}

.sources-section {
  margin-top: 16rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
  padding: 0 8rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #e8e8f0;
}

.section-count {
  font-size: 24rpx;
  color: #5a5a70;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 48rpx 0;
}

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.source-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 16rpx;
  transition: all 0.25s ease;
  animation: fade-in 0.3s ease-out backwards;
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

.sub-btn {
  padding: 12rpx 28rpx;
  background: transparent;
  border: 1px solid #00d4ff;
  border-radius: 10rpx;
  transition: all 0.25s ease;
}

.sub-btn:active {
  background: rgba(0, 212, 255, 0.1);
}

.sub-btn.subscribed {
  background: rgba(168, 85, 247, 0.15);
  border-color: #a855f7;
}

.sub-text {
  font-size: 24rpx;
  font-weight: 500;
  color: #00d4ff;
}

.sub-btn.subscribed .sub-text {
  color: #a855f7;
}

.bottom-padding {
  height: 32rpx;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(16rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>