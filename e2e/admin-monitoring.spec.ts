import { test, expect } from './fixtures';

test.describe('管理后台 - 数据监控', () => {
  test.beforeEach(async ({ authenticatedAdmin: page }) => {
    await page.goto('/admin/monitoring');
  });

  test('页面元素完整性检查', async ({ authenticatedAdmin: page }) => {
    // 系统状态卡片
    await expect(page.locator('text=API服务')).toBeVisible();
    await expect(page.locator('text=撮合引擎')).toBeVisible();
    await expect(page.locator('text=数据库')).toBeVisible();
    await expect(page.locator('text=AI服务')).toBeVisible();
    
    // 实时交易量图表
    await expect(page.locator('text=实时交易量')).toBeVisible();
    
    // 系统资源使用
    await expect(page.locator('text=系统资源使用')).toBeVisible();
    await expect(page.locator('text=CPU')).toBeVisible();
    await expect(page.locator('text=内存')).toBeVisible();
    await expect(page.locator('text=磁盘')).toBeVisible();
    await expect(page.locator('text=网络带宽')).toBeVisible();
    
    // 实时日志
    await expect(page.locator('text=实时日志')).toBeVisible();
  });

  test('系统状态卡片展示', async ({ authenticatedAdmin: page }) => {
    // 验证4个系统状态卡片
    const statusCards = page.locator('.quantum-card').filter({ hasText: /API服务|撮合引擎|数据库|AI服务/ });
    expect(await statusCards.count()).toBe(4);
    
    // 验证状态显示
    await aiAssert(page, '每个系统状态卡片都显示了运行状态，如正常或异常');
  });

  test('实时交易量图表开发中标识', async ({ authenticatedAdmin: page }) => {
    await expect(page.locator('text=开发中')).toBeVisible();
    await expect(page.locator('text=图表组件开发中')).toBeVisible();
  });

  test('系统资源使用展示', async ({ authenticatedAdmin: page }) => {
    // 验证CPU使用率
    await expect(page.locator('text=CPU')).toBeVisible();
    
    // 验证内存使用率
    await expect(page.locator('text=内存')).toBeVisible();
    
    // 验证磁盘使用率
    await expect(page.locator('text=磁盘')).toBeVisible();
    
    // 验证网络带宽
    await expect(page.locator('text=网络带宽')).toBeVisible();
    
    // 验证进度条
    const progressBars = page.locator('.bg-quantum-border');
    expect(await progressBars.count()).toBeGreaterThanOrEqual(4);
  });

  test('CPU使用率进度条', async ({ authenticatedAdmin: page }) => {
    // 验证CPU进度条有数值
    const cpuUsage = await aiQuery(page, '获取CPU使用率的数值');
    expect(cpuUsage).toBeTruthy();
  });

  test('内存使用率进度条', async ({ authenticatedAdmin: page }) => {
    // 验证内存进度条有数值
    const memoryUsage = await aiQuery(page, '获取内存使用率的数值');
    expect(memoryUsage).toBeTruthy();
  });

  test('实时日志列表展示', async ({ authenticatedAdmin: page }) => {
    // 验证有日志数据
    const logItems = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /INFO|WARN|ERROR/ });
    expect(await logItems.count()).toBeGreaterThan(0);
    
    // 验证日志级别
    await aiAssert(page, '实时日志列表中显示了日志级别，如INFO、WARN、ERROR');
  });

  test('日志级别筛选功能', async ({ authenticatedAdmin: page }) => {
    const select = page.locator('select').first();
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在日志级别筛选中选择ERROR');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('导出日志功能', async ({ authenticatedAdmin: page }) => {
    // 点击导出日志
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('导出');
      dialog.accept();
    });
    
    await midscene(page, '点击导出日志按钮');
  });

  test('系统状态颜色标识', async ({ authenticatedAdmin: page }) => {
    // 验证正常状态为绿色
    await aiAssert(page, '正常运行的系统服务显示为绿色状态标识');
  });

  test('日志级别颜色标识', async ({ authenticatedAdmin: page }) => {
    // 验证不同日志级别有不同颜色
    await aiAssert(page, '不同级别的日志有不同的颜色标识，ERROR为红色，WARN为黄色，INFO为蓝色');
  });
});
