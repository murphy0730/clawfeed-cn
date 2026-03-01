<template>
  <view class="page-container">
    <!-- Loading -->
    <view v-if="loading" class="loading-wrapper">
      <XLoading text="加载中..." :size="64" />
    </view>

    <!-- Pack list -->
    <view v-else class="content-wrapper">
      <!-- Empty -->
      <XEmpty
        v-if="!packs.length"
        icon="📦"
        title="暂无 Pack"
        description="Pack 是信息源的合集，可以一键安装多个信息源"
      />

      <!-- Pack cards -->
      <view v-else class="packs-list">
        <view
          v-for="(pack, index) in packs"
          :key="pack.id"
          class="pack-card"
          :style="{ animationDelay: index * 0.05 + 's' }"
          @click="goDetail(pack.slug)"
        >
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
  padding: 24rpx;
}

.packs-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.pack-card {
  padding: 24rpx;
  background: #13131a;
  border: 1px solid #2a2a3a;
  border-radius: 20rpx;
  transition: all 0.25s ease;
  animation: fade-in 0.3s ease-out backwards;
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