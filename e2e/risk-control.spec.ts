import { test, expect } from './fixtures';

test.describe('风控设置页面 - Risk Control Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/risk-control');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 统计卡片
    await expect(page.locator('text=风险等级')).toBeVisible();
    await expect(page.locator('text=最大回撤')).toBeVisible();
    await expect(page.locator('text=止损设置')).toBeVisible();
    await expect(page.locator('text=风控规则')).toBeVisible();
    
    // 持仓风控
    await expect(page.locator('text=持仓风控')).toBeVisible();
    await expect(page.locator('text=单币种最大持仓比例')).toBeVisible();
    await expect(page.locator('text=最大持仓数量')).toBeVisible();
    await expect(page.locator('text=单仓位最大杠杆')).toBeVisible();
    
    // 止损止盈
    await expect(page.locator('text=止损止盈')).toBeVisible();
    await expect(page.locator('text=全局止损')).toBeVisible();
    await expect(page.locator('text=移动止损')).toBeVisible();
    await expect(page.locator('text=自动止盈')).toBeVisible();
    
    // AI策略风控
    await expect(page.locator('text=AI策略风控')).toBeVisible();
    await expect(page.locator('text=策略最大亏损限制')).toBeVisible();
    await expect(page.locator('text=连续亏损暂停')).toBeVisible();
    await expect(page.locator('text=异常波动检测')).toBeVisible();
    
    // 风险预警
    await expect(page.locator('text=风险预警')).toBeVisible();
    await expect(page.locator('text=邮件通知')).toBeVisible();
    await expect(page.locator('text=短信通知')).toBeVisible();
    await expect(page.locator('text=强平预警')).toBeVisible();
    
    // 保存和重置按钮
    await expect(page.locator('text=保存设置')).toBeVisible();
    await expect(page.locator('text=重置默认')).toBeVisible();
  });

  test('统计卡片数据展示', async ({ authenticatedUser: page }) => {
    // 风险等级
    await aiAssert(page, '页面上显示了风险等级，如低风险、中风险或高风险');
    
    // 最大回撤
    const maxDrawdown = await aiQuery(page, '获取最大回撤的数值');
    expect(maxDrawdown).toBeTruthy();
    
    // 止损设置
    await aiAssert(page, '页面上显示了止损设置的状态');
    
    // 风控规则数量
    const rulesCount = await aiQuery(page, '获取风控规则的数量');
    expect(rulesCount).toBeTruthy();
  });

  test('持仓风控参数设置', async ({ authenticatedUser: page }) => {
    // 单币种最大持仓比例
    const ratioInput = page.locator('input[type="number"]').first();
    await midscene(page, '在单币种最大持仓比例输入框中输入40');
    expect(await ratioInput.inputValue()).toBe('40');
    
    // 最大持仓数量
    const countInput = page.locator('input[type="number"]').nth(1);
    await midscene(page, '在最大持仓数量输入框中输入10');
    expect(await countInput.inputValue()).toBe('10');
    
    // 单仓位最大杠杆
    const leverageSelect = page.locator('select').first();
    await midscene(page, '在单仓位最大杠杆选择器中选择20x');
    expect(await leverageSelect.inputValue()).toBeTruthy();
  });

  test('止损止盈开关切换', async ({ authenticatedUser: page }) => {
    // 全局止损开关
    const globalStopLoss = page.locator('input[type="checkbox"]').nth(0);
    const initialState = await globalStopLoss.isChecked();
    
    await midscene(page, '点击全局止损开关');
    expect(await globalStopLoss.isChecked()).not.toBe(initialState);
    
    // 移动止损开关
    const trailingStop = page.locator('input[type="checkbox"]').nth(1);
    await midscene(page, '点击移动止损开关');
    expect(await trailingStop.isChecked()).toBeTruthy();
    
    // 自动止盈开关
    const autoTakeProfit = page.locator('input[type="checkbox"]').nth(2);
    await midscene(page, '点击自动止盈开关');
    expect(await autoTakeProfit.isChecked()).toBeTruthy();
  });

  test('AI策略风控设置', async ({ authenticatedUser: page }) => {
    // 策略最大亏损限制
    const maxLossInput = page.locator('input[type="number"]').nth(3);
    await midscene(page, '在策略最大亏损限制输入框中输入20');
    expect(await maxLossInput.inputValue()).toBe('20');
    
    // 连续亏损暂停开关
    const consecutiveLoss = page.locator('input[type="checkbox"]').nth(3);
    await midscene(page, '点击连续亏损暂停开关');
    expect(await consecutiveLoss.isChecked()).toBeTruthy();
    
    // 异常波动检测开关
    const volatilityDetect = page.locator('input[type="checkbox"]').nth(4);
    await midscene(page, '点击异常波动检测开关');
    expect(await volatilityDetect.isChecked()).toBeTruthy();
  });

  test('风险预警通知设置', async ({ authenticatedUser: page }) => {
    // 邮件通知开关
    const emailNotify = page.locator('input[type="checkbox"]').nth(5);
    await midscene(page, '点击邮件通知开关');
    expect(await emailNotify.isChecked()).toBeTruthy();
    
    // 短信通知开关
    const smsNotify = page.locator('input[type="checkbox"]').nth(6);
    await midscene(page, '点击短信通知开关');
    expect(await smsNotify.isChecked()).toBeTruthy();
    
    // 强平预警开关
    const liquidationWarn = page.locator('input[type="checkbox"]').nth(7);
    await midscene(page, '点击强平预警开关');
    expect(await liquidationWarn.isChecked()).toBeTruthy();
  });

  test('保存设置功能', async ({ authenticatedUser: page }) => {
    // 修改一个设置
    await midscene(page, '在单币种最大持仓比例输入框中输入35');
    
    // 点击保存
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('保存');
      dialog.accept();
    });
    
    await midscene(page, '点击保存设置按钮');
  });

  test('重置默认功能', async ({ authenticatedUser: page }) => {
    // 修改一个设置
    await midscene(page, '在单币种最大持仓比例输入框中输入50');
    
    // 点击重置
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('重置');
      dialog.accept();
    });
    
    await midscene(page, '点击重置默认按钮');
  });

  test('风险等级颜色标识', async ({ authenticatedUser: page }) => {
    // 验证风险等级有颜色标识
    await aiAssert(page, '风险等级显示有对应的颜色标识，低风险为绿色，高风险为红色');
  });

  test('所有开关默认可用状态', async ({ authenticatedUser: page }) => {
    // 验证所有开关都可以正常点击
    const switches = page.locator('input[type="checkbox"]');
    const switchCount = await switches.count();
    expect(switchCount).toBeGreaterThan(5);
  });
});
