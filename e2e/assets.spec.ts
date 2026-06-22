import { test, expect } from './fixtures';

test.describe('资产页面 - Assets Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/assets');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 统计卡片
    await expect(page.locator('text=总资产估值')).toBeVisible();
    await expect(page.locator('text=可用余额')).toBeVisible();
    await expect(page.locator('text=持仓市值')).toBeVisible();
    await expect(page.locator('text=累计盈亏')).toBeVisible();
    
    // 资产明细
    await expect(page.locator('text=资产明细')).toBeVisible();
    
    // 资产分布图表
    await expect(page.locator('text=资产分布')).toBeVisible();
    
    // 资金流水
    await expect(page.locator('text=资金流水')).toBeVisible();
  });

  test('统计卡片数据真实性验证', async ({ authenticatedUser: page }) => {
    // 总资产估值
    const totalAssets = await aiQuery(page, '获取总资产估值的数值');
    expect(totalAssets).toBeTruthy();
    
    // 可用余额
    const availableBalance = await aiQuery(page, '获取可用余额的数值');
    expect(availableBalance).toBeTruthy();
    
    // 持仓市值
    const positionValue = await aiQuery(page, '获取持仓市值的数值');
    expect(positionValue).toBeTruthy();
    
    // 累计盈亏
    const totalPnl = await aiQuery(page, '获取累计盈亏的数值');
    expect(totalPnl).toBeTruthy();
  });

  test('资产明细列表展示', async ({ authenticatedUser: page }) => {
    // 验证有资产明细数据
    const assetItems = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /USDT|BTC|ETH/ });
    expect(await assetItems.count()).toBeGreaterThan(0);
    
    // 验证每个资产都有数量和估值
    await aiAssert(page, '资产明细列表中每个币种都显示了可用数量和估值');
  });

  test('资产分布图开发中标识验证', async ({ authenticatedUser: page }) => {
    await expect(page.locator('text=开发中')).toBeVisible();
    await expect(page.locator('text=图表组件开发中')).toBeVisible();
  });

  test('资金流水表格展示', async ({ authenticatedUser: page }) => {
    // 验证有资金流水数据
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
    
    // 验证流水类型
    await aiAssert(page, '资金流水表格中显示了流水类型，如充值、提现、交易等');
  });

  test('资金流水类型筛选', async ({ authenticatedUser: page }) => {
    const select = page.locator('select').first();
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在资金流水类型筛选中选择充值');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('盈亏颜色正确性', async ({ authenticatedUser: page }) => {
    // 正盈亏绿色，负盈亏红色
    const greenPnl = page.locator('.text-quantum-green').filter({ hasText: /\+/ });
    const redPnl = page.locator('.text-quantum-red').filter({ hasText: /-/ });
    
    // 至少有一个盈亏数据
    const greenCount = await greenPnl.count();
    const redCount = await redPnl.count();
    expect(greenCount + redCount).toBeGreaterThan(0);
  });

  test('资产币种图标显示', async ({ authenticatedUser: page }) => {
    // 验证有币种图标
    const icons = page.locator('svg').filter({ has: page.locator('text=') });
    expect(await icons.count()).toBeGreaterThan(0);
  });

  test('资金流水金额显示', async ({ authenticatedUser: page }) => {
    // 验证有金额显示
    const amounts = page.locator('text=/\\$|USDT/');
    expect(await amounts.count()).toBeGreaterThan(0);
  });

  test('资金流水时间显示', async ({ authenticatedUser: page }) => {
    // 验证有时间列
    await expect(page.locator('text=时间')).toBeVisible();
    
    // 验证有时间数据
    await aiAssert(page, '资金流水表格中显示了交易时间');
  });
});
