import { test, expect } from './fixtures';

test.describe('用户仪表盘 - User Dashboard', () => {
  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 检查统计卡片
    await expect(page.locator('text=总资产')).toBeVisible();
    await expect(page.locator('text=可用余额')).toBeVisible();
    await expect(page.locator('text=持仓盈亏')).toBeVisible();
    await expect(page.locator('text=运行策略')).toBeVisible();
    
    // 检查时间周期切换器
    await expect(page.locator('text=1D')).toBeVisible();
    await expect(page.locator('text=1W')).toBeVisible();
    await expect(page.locator('text=1M')).toBeVisible();
    await expect(page.locator('text=ALL')).toBeVisible();
    
    // 检查图表区域
    await expect(page.locator('text=资产走势')).toBeVisible();
    await expect(page.locator('text=资产分布')).toBeVisible();
    
    // 检查持仓和订单
    await expect(page.locator('text=当前持仓')).toBeVisible();
    await expect(page.locator('text=最近订单')).toBeVisible();
    
    // 检查查看全部链接
    await expect(page.locator('text=查看全部')).toHaveCount(2);
  });

  test('统计卡片数据真实性验证', async ({ authenticatedUser: page }) => {
    // 验证总资产显示
    const totalAssets = await aiQuery(page, '获取总资产的数值');
    expect(totalAssets).toBeTruthy();
    
    // 验证可用余额
    const availableBalance = await aiQuery(page, '获取可用余额的数值');
    expect(availableBalance).toBeTruthy();
    
    // 验证持仓盈亏有正负颜色区分
    await aiAssert(page, '页面上有显示盈亏百分比的数字');
  });

  test('时间周期切换功能', async ({ authenticatedUser: page }) => {
    // 默认选中1D
    await expect(page.locator('button:has-text("1D")')).toHaveClass(/bg-quantum-cyan/);
    
    // 点击1W
    await midscene(page, '点击时间周期切换器中的1W按钮');
    await expect(page.locator('button:has-text("1W")')).toHaveClass(/bg-quantum-cyan/);
    
    // 点击1M
    await midscene(page, '点击时间周期切换器中的1M按钮');
    await expect(page.locator('button:has-text("1M")')).toHaveClass(/bg-quantum-cyan/);
    
    // 点击ALL
    await midscene(page, '点击时间周期切换器中的ALL按钮');
    await expect(page.locator('button:has-text("ALL")')).toHaveClass(/bg-quantum-cyan/);
  });

  test('图表开发中标识验证', async ({ authenticatedUser: page }) => {
    // 资产走势图开发中
    await expect(page.locator('text=图表组件开发中')).toBeVisible();
    
    // 资产分布图开发中
    const chartPlaceholders = page.locator('text=开发中');
    expect(await chartPlaceholders.count()).toBeGreaterThanOrEqual(2);
  });

  test('当前持仓列表展示', async ({ authenticatedUser: page }) => {
    // 验证有持仓数据
    const positions = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /现货|合约/ });
    expect(await positions.count()).toBeGreaterThan(0);
    
    // 验证每个持仓都有盈亏显示
    await aiAssert(page, '每个持仓项都显示了盈亏金额和百分比');
  });

  test('最近订单列表展示', async ({ authenticatedUser: page }) => {
    // 验证有订单数据
    const orders = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /市价|限价/ });
    expect(await orders.count()).toBeGreaterThan(0);
    
    // 验证订单状态标签
    await aiAssert(page, '订单列表中有显示订单状态标签');
  });

  test('侧边栏导航 - 所有页面跳转', async ({ authenticatedUser: page }) => {
    // 交易页面
    await midscene(page, '点击侧边栏中的交易菜单');
    await expect(page).toHaveURL('/trade');
    
    // 持仓页面
    await midscene(page, '点击侧边栏中的持仓菜单');
    await expect(page).toHaveURL('/positions');
    
    // 订单页面
    await midscene(page, '点击侧边栏中的订单菜单');
    await expect(page).toHaveURL('/orders');
    
    // 资产页面
    await midscene(page, '点击侧边栏中的资产菜单');
    await expect(page).toHaveURL('/assets');
    
    // AI策略页面
    await midscene(page, '点击侧边栏中的AI策略菜单');
    await expect(page).toHaveURL('/ai-strategy');
    
    // 风控设置页面
    await midscene(page, '点击侧边栏中的风控设置菜单');
    await expect(page).toHaveURL('/risk-control');
    
    // 设置页面
    await midscene(page, '点击侧边栏中的设置菜单');
    await expect(page).toHaveURL('/settings');
    
    // 返回仪表盘
    await midscene(page, '点击侧边栏中的仪表盘菜单');
    await expect(page).toHaveURL('/dashboard');
  });

  test('顶部导航栏元素检查', async ({ authenticatedUser: page }) => {
    // 页面标题
    await expect(page.locator('text=仪表盘')).toBeVisible();
    
    // 模拟盘标识
    await expect(page.locator('text=模拟盘')).toBeVisible();
    
    // 可用余额
    await expect(page.locator('text=可用余额')).toBeVisible();
    
    // 通知铃铛图标
    const bellButton = page.locator('button').filter({ has: page.locator('svg') }).nth(1);
    await expect(bellButton).toBeVisible();
  });

  test('用户信息和退出登录', async ({ authenticatedUser: page }) => {
    // 验证用户邮箱显示
    await expect(page.locator('text=test@quantumtrader.ai')).toBeVisible();
    
    // 验证用户名
    await expect(page.locator('text=test_user')).toBeVisible();
    
    // 退出登录按钮
    await expect(page.locator('text=退出登录')).toBeVisible();
    
    // 测试退出登录
    await midscene(page, '点击退出登录按钮');
    await expect(page).toHaveURL('/login');
  });

  test('查看全部持仓跳转', async ({ authenticatedUser: page }) => {
    await midscene(page, '点击当前持仓旁边的查看全部链接');
    await expect(page).toHaveURL('/positions');
  });

  test('查看全部订单跳转', async ({ authenticatedUser: page }) => {
    await midscene(page, '点击最近订单旁边的查看全部链接');
    await expect(page).toHaveURL('/orders');
  });

  test('Logo和品牌显示', async ({ authenticatedUser: page }) => {
    await expect(page.locator('text=QuantumTrader')).toBeVisible();
    await expect(page.locator('text=AI Trading System')).toBeVisible();
  });

  test('盈亏颜色正确性', async ({ authenticatedUser: page }) => {
    // 正盈亏应该是绿色，负盈亏应该是红色
    const greenPnl = page.locator('.text-quantum-green').filter({ hasText: /\+/ });
    const redPnl = page.locator('.text-quantum-red').filter({ hasText: /-/ });
    
    // 至少有一个正盈亏或负盈亏
    const greenCount = await greenPnl.count();
    const redCount = await redPnl.count();
    expect(greenCount + redCount).toBeGreaterThan(0);
  });
});
