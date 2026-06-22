import { test, expect } from './fixtures';

test.describe('管理后台 - 系统设置', () => {
  test.beforeEach(async ({ authenticatedAdmin: page }) => {
    await page.goto('/admin/system');
  });

  test('页面元素完整性检查', async ({ authenticatedAdmin: page }) => {
    // 侧边栏导航
    await expect(page.locator('text=基本设置')).toBeVisible();
    await expect(page.locator('text=交易设置')).toBeVisible();
    await expect(page.locator('text=安全设置')).toBeVisible();
    await expect(page.locator('text=关于系统')).toBeVisible();
  });

  test('基本设置页面展示', async ({ authenticatedAdmin: page }) => {
    // 默认显示基本设置
    await expect(page.locator('text=基本设置')).toBeVisible();
    await expect(page.locator('text=系统名称')).toBeVisible();
    await expect(page.locator('text=系统版本')).toBeVisible();
    await expect(page.locator('text=默认语言')).toBeVisible();
    await expect(page.locator('text=时区')).toBeVisible();
  });

  test('基本设置编辑功能', async ({ authenticatedAdmin: page }) => {
    // 修改系统名称
    const nameInput = page.locator('input[type="text"]').first();
    await midscene(page, '在系统名称输入框中输入QuantumTrader AI Pro');
    expect(await nameInput.inputValue()).toContain('QuantumTrader AI Pro');
    
    // 修改默认语言
    const langSelect = page.locator('select').first();
    await midscene(page, '在默认语言选择器中选择English');
    expect(await langSelect.inputValue()).toBeTruthy();
    
    // 保存设置
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('保存');
      dialog.accept();
    });
    
    await midscene(page, '点击保存按钮');
  });

  test('交易设置页面', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    // 验证交易设置项
    await expect(page.locator('text=开启现货交易')).toBeVisible();
    await expect(page.locator('text=开启合约交易')).toBeVisible();
    await expect(page.locator('text=开启期权交易')).toBeVisible();
    await expect(page.locator('text=AI策略交易')).toBeVisible();
  });

  test('现货交易开关', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    const spotSwitch = page.locator('input[type="checkbox"]').nth(0);
    const initialState = await spotSwitch.isChecked();
    
    await midscene(page, '点击开启现货交易开关');
    expect(await spotSwitch.isChecked()).not.toBe(initialState);
  });

  test('合约交易开关', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    const futuresSwitch = page.locator('input[type="checkbox"]').nth(1);
    await midscene(page, '点击开启合约交易开关');
    expect(await futuresSwitch.isChecked()).toBeTruthy();
  });

  test('期权交易开关', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    const optionsSwitch = page.locator('input[type="checkbox"]').nth(2);
    await midscene(page, '点击开启期权交易开关');
    expect(await optionsSwitch.isChecked()).toBeTruthy();
  });

  test('AI策略交易开关', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    const aiSwitch = page.locator('input[type="checkbox"]').nth(3);
    await midscene(page, '点击AI策略交易开关');
    expect(await aiSwitch.isChecked()).toBeTruthy();
  });

  test('安全设置页面', async ({ authenticatedAdmin: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    // 验证安全设置项
    await expect(page.locator('text=登录失败锁定')).toBeVisible();
    await expect(page.locator('text=IP白名单')).toBeVisible();
    await expect(page.locator('text=操作日志')).toBeVisible();
  });

  test('登录失败锁定设置', async ({ authenticatedAdmin: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    // 设置失败次数
    const failCountInput = page.locator('input[type="number"]').first();
    await midscene(page, '在登录失败锁定次数输入框中输入5');
    expect(await failCountInput.inputValue()).toBe('5');
  });

  test('IP白名单开关', async ({ authenticatedAdmin: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    const ipWhitelistSwitch = page.locator('input[type="checkbox"]').nth(0);
    await midscene(page, '点击IP白名单开关');
    expect(await ipWhitelistSwitch.isChecked()).toBeTruthy();
  });

  test('操作日志开关', async ({ authenticatedAdmin: page }) => {
    // 切换到安全设置
    await midscene(page, '点击侧边栏中的安全设置');
    
    const operationLogSwitch = page.locator('input[type="checkbox"]').nth(1);
    await midscene(page, '点击操作日志开关');
    expect(await operationLogSwitch.isChecked()).toBeTruthy();
  });

  test('关于系统页面', async ({ authenticatedAdmin: page }) => {
    // 切换到关于系统
    await midscene(page, '点击侧边栏中的关于系统');
    
    // 验证系统信息
    await expect(page.locator('text=系统信息')).toBeVisible();
    await expect(page.locator('text=版本')).toBeVisible();
    await expect(page.locator('text=构建时间')).toBeVisible();
    await expect(page.locator('text=技术支持')).toBeVisible();
  });

  test('侧边栏导航切换', async ({ authenticatedAdmin: page }) => {
    // 测试所有导航项
    const navItems = ['基本设置', '交易设置', '安全设置', '关于系统'];
    
    for (const item of navItems) {
      await midscene(page, `点击侧边栏中的${item}`);
      await expect(page.locator(`text=${item}`).first()).toHaveClass(/text-quantum-purple/);
    }
  });

  test('系统版本显示', async ({ authenticatedAdmin: page }) => {
    // 切换到关于系统
    await midscene(page, '点击侧边栏中的关于系统');
    
    // 验证版本号
    await aiAssert(page, '页面上显示了系统版本号');
  });

  test('保存交易设置功能', async ({ authenticatedAdmin: page }) => {
    // 切换到交易设置
    await midscene(page, '点击侧边栏中的交易设置');
    
    // 修改一个开关
    await midscene(page, '点击开启期权交易开关');
    
    // 点击保存
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('保存');
      dialog.accept();
    });
    
    await midscene(page, '点击保存按钮');
  });
});
