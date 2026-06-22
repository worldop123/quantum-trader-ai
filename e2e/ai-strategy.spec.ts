import { test, expect } from './fixtures';

test.describe('AI策略页面 - AI Strategy Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/ai-strategy');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 统计卡片
    await expect(page.locator('text=运行策略')).toBeVisible();
    await expect(page.locator('text=总收益')).toBeVisible();
    await expect(page.locator('text=平均胜率')).toBeVisible();
    await expect(page.locator('text=总交易次数')).toBeVisible();
    
    // 策略列表
    await expect(page.locator('text=我的策略')).toBeVisible();
    
    // 策略模板库
    await expect(page.locator('text=策略模板库')).toBeVisible();
    
    // 创建新策略按钮
    await expect(page.locator('text=创建新策略')).toBeVisible();
  });

  test('统计卡片数据真实性验证', async ({ authenticatedUser: page }) => {
    // 运行策略数
    const runningStrategies = await aiQuery(page, '获取运行策略的数量');
    expect(runningStrategies).toBeTruthy();
    
    // 总收益
    const totalProfit = await aiQuery(page, '获取总收益的数值');
    expect(totalProfit).toBeTruthy();
    
    // 平均胜率
    const winRate = await aiQuery(page, '获取平均胜率的数值');
    expect(winRate).toBeTruthy();
    
    // 总交易次数
    const totalTrades = await aiQuery(page, '获取总交易次数的数值');
    expect(totalTrades).toBeTruthy();
  });

  test('策略列表展示', async ({ authenticatedUser: page }) => {
    // 验证有策略数据
    const strategyCards = page.locator('.quantum-card').filter({ hasText: /网格交易|趋势追踪|均值回归/ });
    expect(await strategyCards.count()).toBeGreaterThan(0);
    
    // 验证每个策略都有状态
    await aiAssert(page, '每个策略卡片都显示了运行状态，如运行中或已停止');
  });

  test('策略启停功能', async ({ authenticatedUser: page }) => {
    // 找到第一个策略的开关
    const firstStrategy = page.locator('.quantum-card').filter({ hasText: /网格交易|趋势追踪/ }).first();
    
    // 点击开关
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('策略');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个策略的启停开关');
  });

  test('创建新策略按钮', async ({ authenticatedUser: page }) => {
    // 点击创建新策略
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('创建');
      dialog.accept();
    });
    
    await midscene(page, '点击创建新策略按钮');
  });

  test('策略模板库展示', async ({ authenticatedUser: page }) => {
    // 验证有4个策略模板
    const templates = page.locator('.quantum-card').filter({ hasText: /网格交易|趋势追踪|均值回归|套利策略/ });
    expect(await templates.count()).toBe(4);
    
    // 验证每个模板都有描述
    await aiAssert(page, '每个策略模板都有简短的功能描述');
  });

  test('策略模板使用功能', async ({ authenticatedUser: page }) => {
    // 点击使用模板
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('使用');
      dialog.accept();
    });
    
    await midscene(page, '点击网格交易模板的使用按钮');
  });

  test('策略收益显示', async ({ authenticatedUser: page }) => {
    // 验证有收益显示
    const profitText = page.locator('text=/收益|盈利/');
    expect(await profitText.count()).toBeGreaterThan(0);
    
    // 验证盈亏颜色
    await aiAssert(page, '正收益显示为绿色，负收益显示为红色');
  });

  test('策略运行时间显示', async ({ authenticatedUser: page }) => {
    // 验证有运行时间
    await aiAssert(page, '策略卡片中显示了运行时间或运行天数');
  });

  test('策略交易对显示', async ({ authenticatedUser: page }) => {
    // 验证有交易对信息
    await aiAssert(page, '策略卡片中显示了适用的交易对');
  });
});
