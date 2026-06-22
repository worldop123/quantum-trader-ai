import { test, expect } from './fixtures';

test.describe('管理后台仪表盘 - Admin Dashboard', () => {
  test.beforeEach(async ({ authenticatedAdmin: page }) => {
    await page.goto('/admin/dashboard');
  });

  test('页面元素完整性检查', async ({ authenticatedAdmin: page }) => {
    // 统计卡片
    await expect(page.locator('text=总用户数')).toBeVisible();
    await expect(page.locator('text=总交易量')).toBeVisible();
    await expect(page.locator('text=运行策略')).toBeVisible();
    await expect(page.locator('text=系统状态')).toBeVisible();
    
    // 图表区域
    await expect(page.locator('text=用户增长趋势')).toBeVisible();
    await expect(page.locator('text=交易量分布')).toBeVisible();
    
    // 列表区域
    await expect(page.locator('text=最近注册用户')).toBeVisible();
    await expect(page.locator('text=系统告警')).toBeVisible();
  });

  test('统计卡片数据真实性验证', async ({ authenticatedAdmin: page }) => {
    // 总用户数
    const totalUsers = await aiQuery(page, '获取总用户数的数值');
    expect(totalUsers).toBeTruthy();
    
    // 总交易量
    const totalVolume = await aiQuery(page, '获取总交易量的数值');
    expect(totalVolume).toBeTruthy();
    
    // 运行策略数
    const runningStrategies = await aiQuery(page, '获取运行策略的数量');
    expect(runningStrategies).toBeTruthy();
    
    // 系统状态
    await aiAssert(page, '页面上显示了系统状态，如正常或异常');
  });

  test('用户增长趋势图开发中标识', async ({ authenticatedAdmin: page }) => {
    await expect(page.locator('text=开发中')).toBeVisible();
    await expect(page.locator('text=图表组件开发中')).toBeVisible();
  });

  test('交易量分布图开发中标识', async ({ authenticatedAdmin: page }) => {
    const chartPlaceholders = page.locator('text=开发中');
    expect(await chartPlaceholders.count()).toBeGreaterThanOrEqual(2);
  });

  test('最近注册用户列表展示', async ({ authenticatedAdmin: page }) => {
    // 验证有用户数据
    const userItems = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /@/ });
    expect(await userItems.count()).toBeGreaterThan(0);
    
    // 验证用户信息
    await aiAssert(page, '最近注册用户列表中显示了用户名和邮箱');
  });

  test('系统告警列表展示', async ({ authenticatedAdmin: page }) => {
    // 验证有告警数据
    const alertItems = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /告警|警告|错误/ });
    expect(await alertItems.count()).toBeGreaterThan(0);
    
    // 验证告警级别
    await aiAssert(page, '系统告警列表中显示了告警级别，如高危、中危、低危');
  });

  test('侧边栏导航 - 所有页面跳转', async ({ authenticatedAdmin: page }) => {
    // 用户管理
    await midscene(page, '点击侧边栏中的用户管理菜单');
    await expect(page).toHaveURL('/admin/users');
    
    // 数据监控
    await midscene(page, '点击侧边栏中的数据监控菜单');
    await expect(page).toHaveURL('/admin/monitoring');
    
    // 风控管理
    await midscene(page, '点击侧边栏中的风控管理菜单');
    await expect(page).toHaveURL('/admin/risk');
    
    // 系统设置
    await midscene(page, '点击侧边栏中的系统设置菜单');
    await expect(page).toHaveURL('/admin/system');
    
    // 返回数据概览
    await midscene(page, '点击侧边栏中的数据概览菜单');
    await expect(page).toHaveURL('/admin/dashboard');
  });

  test('管理员标识显示', async ({ authenticatedAdmin: page }) => {
    await expect(page.locator('text=管理员')).toBeVisible();
  });

  test('系统状态指示灯', async ({ authenticatedAdmin: page }) => {
    // 验证有系统状态指示灯
    await expect(page.locator('text=系统正常')).toBeVisible();
    
    // 验证有脉冲动画
    const pulseDot = page.locator('.animate-pulse');
    expect(await pulseDot.count()).toBeGreaterThan(0);
  });

  test('管理员信息显示', async ({ authenticatedAdmin: page }) => {
    // 验证管理员邮箱
    await expect(page.locator('text=admin@quantumtrader.ai')).toBeVisible();
    
    // 验证管理员用户名
    await expect(page.locator('text=admin')).toBeVisible();
  });

  test('退出登录功能', async ({ authenticatedAdmin: page }) => {
    await midscene(page, '点击退出登录按钮');
    await expect(page).toHaveURL('/login');
  });

  test('紫色主题验证', async ({ authenticatedAdmin: page }) => {
    // 验证管理后台使用紫色主题
    const purpleElements = page.locator('.text-quantum-purple');
    expect(await purpleElements.count()).toBeGreaterThan(0);
  });

  test('Logo和品牌显示', async ({ authenticatedAdmin: page }) => {
    await expect(page.locator('text=Admin Panel')).toBeVisible();
    await expect(page.locator('text=QuantumTrader AI')).toBeVisible();
  });
});
