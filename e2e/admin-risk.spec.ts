import { test, expect } from './fixtures';

test.describe('管理后台 - 风控管理', () => {
  test.beforeEach(async ({ authenticatedAdmin: page }) => {
    await page.goto('/admin/risk');
  });

  test('页面元素完整性检查', async ({ authenticatedAdmin: page }) => {
    // 统计卡片
    await expect(page.locator('text=系统风险等级')).toBeVisible();
    await expect(page.locator('text=待处理告警')).toBeVisible();
    await expect(page.locator('text=今日强平')).toBeVisible();
    await expect(page.locator('text=风控规则')).toBeVisible();
    
    // 全局风控参数
    await expect(page.locator('text=全局风控参数')).toBeVisible();
    await expect(page.locator('text=单用户最大持仓比例')).toBeVisible();
    await expect(page.locator('text=单币种最大持仓')).toBeVisible();
    await expect(page.locator('text=最大杠杆倍数')).toBeVisible();
    await expect(page.locator('text=异常波动检测')).toBeVisible();
    
    // 最近风控事件
    await expect(page.locator('text=最近风控事件')).toBeVisible();
    
    // 风控规则管理
    await expect(page.locator('text=风控规则管理')).toBeVisible();
  });

  test('统计卡片数据展示', async ({ authenticatedAdmin: page }) => {
    // 系统风险等级
    await aiAssert(page, '页面上显示了系统风险等级，如低风险、中风险或高风险');
    
    // 待处理告警数
    const pendingAlerts = await aiQuery(page, '获取待处理告警的数量');
    expect(pendingAlerts).toBeTruthy();
    
    // 今日强平数
    const liquidations = await aiQuery(page, '获取今日强平的数量');
    expect(liquidations).toBeTruthy();
    
    // 风控规则数
    const rulesCount = await aiQuery(page, '获取风控规则的数量');
    expect(rulesCount).toBeTruthy();
  });

  test('全局风控参数设置', async ({ authenticatedAdmin: page }) => {
    // 单用户最大持仓比例
    const ratioInput = page.locator('input[type="number"]').first();
    await midscene(page, '在单用户最大持仓比例输入框中输入50');
    expect(await ratioInput.inputValue()).toBe('50');
    
    // 单币种最大持仓
    const positionInput = page.locator('input[type="number"]').nth(1);
    await midscene(page, '在单币种最大持仓输入框中输入100');
    expect(await positionInput.inputValue()).toBe('100');
    
    // 最大杠杆倍数
    const leverageSelect = page.locator('select').first();
    await midscene(page, '在最大杠杆倍数选择器中选择50x');
    expect(await leverageSelect.inputValue()).toBeTruthy();
  });

  test('异常波动检测开关', async ({ authenticatedAdmin: page }) => {
    const volatilitySwitch = page.locator('input[type="checkbox"]').first();
    const initialState = await volatilitySwitch.isChecked();
    
    await midscene(page, '点击异常波动检测开关');
    expect(await volatilitySwitch.isChecked()).not.toBe(initialState);
  });

  test('最近风控事件列表展示', async ({ authenticatedAdmin: page }) => {
    // 验证有风控事件数据
    const eventItems = page.locator('.bg-quantum-darker.rounded-lg').filter({ hasText: /风控|告警|强平/ });
    expect(await eventItems.count()).toBeGreaterThan(0);
    
    // 验证事件信息
    await aiAssert(page, '最近风控事件列表中显示了事件类型、时间和详情');
  });

  test('风控规则管理表格展示', async ({ authenticatedAdmin: page }) => {
    // 验证有规则数据
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
    
    // 验证规则列
    await expect(page.locator('text=规则名称')).toBeVisible();
    await expect(page.locator('text=类型')).toBeVisible();
    await expect(page.locator('text=触发条件')).toBeVisible();
    await expect(page.locator('text=执行动作')).toBeVisible();
    await expect(page.locator('text=状态')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
  });

  test('风控规则状态开关', async ({ authenticatedAdmin: page }) => {
    const ruleSwitch = page.locator('input[type="checkbox"]').nth(1);
    const initialState = await ruleSwitch.isChecked();
    
    await midscene(page, '点击第一个风控规则的状态开关');
    expect(await ruleSwitch.isChecked()).not.toBe(initialState);
  });

  test('编辑风控规则功能', async ({ authenticatedAdmin: page }) => {
    // 点击编辑
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('编辑');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个风控规则的编辑按钮');
  });

  test('删除风控规则功能', async ({ authenticatedAdmin: page }) => {
    // 点击删除
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('删除');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个风控规则的删除按钮');
  });

  test('风险等级颜色标识', async ({ authenticatedAdmin: page }) => {
    // 验证风险等级有颜色标识
    await aiAssert(page, '系统风险等级显示有对应的颜色标识，低风险为绿色，高风险为红色');
  });

  test('风控事件级别颜色标识', async ({ authenticatedAdmin: page }) => {
    // 验证不同级别事件有不同颜色
    await aiAssert(page, '不同级别的风控事件有不同的颜色标识，高危为红色，中危为黄色，低危为蓝色');
  });

  test('保存全局风控参数功能', async ({ authenticatedAdmin: page }) => {
    // 修改一个参数
    await midscene(page, '在单用户最大持仓比例输入框中输入45');
    
    // 点击保存
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('保存');
      dialog.accept();
    });
    
    await midscene(page, '点击保存按钮');
  });
});
