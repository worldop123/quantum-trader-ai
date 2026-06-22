import { test, expect } from './fixtures';

test.describe('订单页面 - Orders Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/orders');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 状态标签
    await expect(page.locator('text=全部')).toBeVisible();
    await expect(page.locator('text=进行中')).toBeVisible();
    await expect(page.locator('text=已成交')).toBeVisible();
    await expect(page.locator('text=已取消')).toBeVisible();
    
    // 筛选器
    await expect(page.locator('select')).first().toBeVisible();
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    
    // 表格列
    await expect(page.locator('text=订单ID')).toBeVisible();
    await expect(page.locator('text=交易对')).toBeVisible();
    await expect(page.locator('text=类型')).toBeVisible();
    await expect(page.locator('text=方向')).toBeVisible();
    await expect(page.locator('text=价格')).toBeVisible();
    await expect(page.locator('text=数量')).toBeVisible();
    await expect(page.locator('text=已成交')).toBeVisible();
    await expect(page.locator('text=状态')).toBeVisible();
    await expect(page.locator('text=时间')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
  });

  test('状态标签切换 - 全部/进行中/已成交/已取消', async ({ authenticatedUser: page }) => {
    // 默认全部
    await expect(page.locator('text=全部').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到进行中
    await midscene(page, '点击进行中标签');
    await expect(page.locator('text=进行中').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到已成交
    await midscene(page, '点击已成交标签');
    await expect(page.locator('text=已成交').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到已取消
    await midscene(page, '点击已取消标签');
    await expect(page.locator('text=已取消').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切回全部
    await midscene(page, '点击全部标签');
    await expect(page.locator('text=全部').first()).toHaveClass(/bg-quantum-cyan/);
  });

  test('进行中标签显示全部取消按钮', async ({ authenticatedUser: page }) => {
    // 切换到进行中
    await midscene(page, '点击进行中标签');
    
    // 验证全部取消按钮
    await expect(page.locator('text=全部取消')).toBeVisible();
  });

  test('方向筛选功能', async ({ authenticatedUser: page }) => {
    const select = page.locator('select').first();
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在方向筛选中选择买入');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('搜索交易对功能', async ({ authenticatedUser: page }) => {
    const searchInput = page.locator('input[type="text"]').first();
    
    // 输入搜索内容
    await midscene(page, '在搜索框中输入ETH');
    const value = await searchInput.inputValue();
    expect(value).toContain('ETH');
  });

  test('订单表格数据展示', async ({ authenticatedUser: page }) => {
    // 验证有订单数据
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
    
    // 验证订单状态标签
    await aiAssert(page, '订单表格中显示了订单状态标签');
  });

  test('取消订单功能 - 正常流程', async ({ authenticatedUser: page }) => {
    // 切换到进行中
    await midscene(page, '点击进行中标签');
    
    // 找到第一个取消按钮
    const cancelButton = page.locator('text=取消').first();
    
    // 点击取消
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('取消');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个订单的取消按钮');
  });

  test('全部取消功能', async ({ authenticatedUser: page }) => {
    // 切换到进行中
    await midscene(page, '点击进行中标签');
    
    // 点击全部取消
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('全部取消');
      dialog.accept();
    });
    
    await midscene(page, '点击全部取消按钮');
  });

  test('订单状态颜色正确性', async ({ authenticatedUser: page }) => {
    // 验证有状态标签
    const statusTags = page.locator('.px-2.py-1.text-xs.rounded');
    expect(await statusTags.count()).toBeGreaterThan(0);
    
    // 验证不同状态有不同颜色
    await aiAssert(page, '订单表格中不同状态的订单有不同的颜色标识');
  });

  test('分页功能', async ({ authenticatedUser: page }) => {
    // 检查分页元素
    const pagination = page.locator('.flex.items-center.gap-2').last();
    await expect(pagination).toBeVisible();
    
    // 验证有上一页/下一页按钮
    await expect(page.locator('text=上一页')).toBeVisible();
    await expect(page.locator('text=下一页')).toBeVisible();
  });

  test('订单类型显示 - 市价/限价', async ({ authenticatedUser: page }) => {
    // 验证有类型列
    await expect(page.locator('text=类型')).toBeVisible();
    
    // 验证显示市价或限价
    await aiAssert(page, '订单表格中显示了市价或限价的订单类型');
  });

  test('方向显示 - 买入/卖出', async ({ authenticatedUser: page }) => {
    // 验证有方向列
    await expect(page.locator('text=方向')).toBeVisible();
    
    // 验证有买入或卖出标识
    await aiAssert(page, '订单表格中显示了买入或卖出的方向标识');
  });
});
