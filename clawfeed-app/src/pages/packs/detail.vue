<template>
  <view class="page-container">
    <!-- Loading -->
    <view v-if="loading" class="loading-wrapper">
      <XLoading text="加载中..." :size="64" />
    </view>

    <!-- Content -->
    <view v-else-if="pack" class="content-wrapper">
      <!-- Header -->
      <view class="header">
        <view class="header-bg"></view>
        <view class="header-content">
          <view class="pack-icon-large">
            <text class="icon-text">📦</text>
          </view>
          <text class="pack-name">{{ pack.name }}</text>
          <text class="pack-creator">by {{ pack.creator_name || "匿名" }}</text>
        </view>
      </view>

      <!-- Description -->
      <view class="desc-section">
        <text class="pack-desc">{{ pack.description || "暂无描述" }}</text>
      </view>

      <!-- Sources list -->
      <view class="sources-section">
        <view class="section-header">
          <text class="section-title">包含的信息源</text>
          <text class="section-count">{{ (pack.sources || []).length }} 个</text>
        </view>

        <view v-if="pack.sources && pack.sources.length" class="sources-list">
          <view
            v-for="(s, i) in pack.sources"
            :key="i"
            class="source-item"
            :style="{ animationDelay: i * 0.03 + 's' }"
          >
            <view class="source-icon-wrap">
              <text class="source-icon">{{ s.icon || "📡" }}</text>
            </view>
            <view class="source-info">
              <text class="source-name">{{ s.name }}</text>
              <text class="source-type">{{ s.type }}</text>
            </view>
          </view>
        </view>
        <XEmpty v-else icon="📡" title="暂无信息源" />
      </view>

      <!-- Install button -->
      <view class="install-section">
        <view
          class="install-btn"
          :class="{ installing: installing }"
          @click="install"
        >
          <text v-if="!installing" class="install-text">一键安装</text>
          <view v-else class="install-spinner"></view>
        </view>
      </view>
    </view>

    <!-- Empty -->
    <XEmpty v-else icon="📦" title="Pack 不存在" />
  </view>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { useApi } from "../../composables/useApi";
import XLoading from "../../components/XLoading.vue";
import XEmpty from "../../components/XEmpty.vue";

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
  if (!slug || installing.value) return;
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

<style lang="scss" scoped>
.page-container {
  min-height: 100vh;
  background: #0a0a0f;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  padding: 120rpx 0;
}

.content-wrapper {
  min-height: 100vh;
}

.header {
  position: relative;
  padding: 48rpx 24rpx;
  overflow: hidden;
}

.header-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(168, 85, 247, 0.15));
  opacity: 0.6;
}

.header-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pack-icon-large {
  width: 100rpx;
  height: 100rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(0, 212, 255, 0.3);
  border-radius: 24rpx;
  margin-bottom: 20rpx;
}

.icon-text {
  font-size: 48rpx;
}

.pack-name {
  font-size: 40rpx;
  font-weight: 700;
  color: #e8e8f0;
  margin-bottom: 8rpx;
}

.pack-creator {
  font-size: 26rpx;
  color: #8888a0;
}

.desc-section {
  padding: 0 24rpx 24rpx;
}

.pack-desc {
  font-size: 28rpx;
  color: #8888a0;
  line-height: 1.7;
}

.sources-section {
  padding: 0 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
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

.sources-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.source-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 16rpx;
  animation: fade-in 0.3s ease-out backwards;
}

.source-icon-wrap {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 12rpx;
}

.source-icon {
  font-size: 28rpx;
}

.source-info {
  flex: 1;
}

.source-name {
  display: block;
  font-size: 28rpx;
  color: #e8e8f0;
  font-weight: 500;
  margin-bottom: 4rpx;
}

.source-type {
  display: block;
  font-size: 22rpx;
  color: #5a5a70;
}

.install-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx;
  background: rgba(10, 10, 15, 0.95);
  border-top: 1px solid #2a2a3a;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.install-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28rpx 0;
  background: linear-gradient(135deg, #00d4ff, #a855f7);
  border-radius: 20rpx;
  transition: all 0.25s ease;
}

.install-btn:active {
  transform: scale(0.98);
  opacity: 0.9;
}

.install-btn.installing {
  opacity: 0.7;
}

.install-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #ffffff;
}

.install-spinner {
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

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(12rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>