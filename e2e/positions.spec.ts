import { test, expect } from './fixtures';

test.describe('持仓页面 - Positions Page', () => {
  test.beforeEach(async ({ authenticatedUser: page }) => {
    await page.goto('/positions');
  });

  test('页面元素完整性检查', async ({ authenticatedUser: page }) => {
    // 标签切换
    await expect(page.locator('text=全部')).toBeVisible();
    await expect(page.locator('text=现货')).toBeVisible();
    await expect(page.locator('text=合约')).toBeVisible();
    await expect(page.locator('text=期权')).toBeVisible();
    
    // 筛选器
    await expect(page.locator('select')).first().toBeVisible();
    await expect(page.locator('input[type="text"]').first()).toBeVisible();
    
    // 表格列
    await expect(page.locator('text=交易对')).toBeVisible();
    await expect(page.locator('text=类型')).toBeVisible();
    await expect(page.locator('text=方向')).toBeVisible();
    await expect(page.locator('text=数量')).toBeVisible();
    await expect(page.locator('text=开仓价')).toBeVisible();
    await expect(page.locator('text=当前价')).toBeVisible();
    await expect(page.locator('text=盈亏')).toBeVisible();
    await expect(page.locator('text=盈亏率')).toBeVisible();
    await expect(page.locator('text=操作')).toBeVisible();
    
    // 统计卡片
    await expect(page.locator('text=持仓总数')).toBeVisible();
    await expect(page.locator('text=总盈亏')).toBeVisible();
    await expect(page.locator('text=保证金占用')).toBeVisible();
  });

  test('标签切换功能 - 全部/现货/合约/期权', async ({ authenticatedUser: page }) => {
    // 默认全部
    await expect(page.locator('text=全部').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到现货
    await midscene(page, '点击现货标签');
    await expect(page.locator('text=现货').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到合约
    await midscene(page, '点击合约标签');
    await expect(page.locator('text=合约').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切换到期权
    await midscene(page, '点击期权标签');
    await expect(page.locator('text=期权').first()).toHaveClass(/bg-quantum-cyan/);
    
    // 切回全部
    await midscene(page, '点击全部标签');
    await expect(page.locator('text=全部').first()).toHaveClass(/bg-quantum-cyan/);
  });

  test('类型筛选功能', async ({ authenticatedUser: page }) => {
    const select = page.locator('select').first();
    
    // 验证有筛选选项
    const options = select.locator('option');
    expect(await options.count()).toBeGreaterThan(1);
    
    // 切换筛选
    await midscene(page, '在类型筛选中选择现货');
    expect(await select.inputValue()).toBeTruthy();
  });

  test('搜索交易对功能', async ({ authenticatedUser: page }) => {
    const searchInput = page.locator('input[type="text"]').first();
    
    // 输入搜索内容
    await midscene(page, '在搜索框中输入BTC');
    const value = await searchInput.inputValue();
    expect(value).toContain('BTC');
    
    // 清空搜索
    await midscene(page, '清空搜索框内容');
    expect(await searchInput.inputValue()).toBe('');
  });

  test('持仓表格数据展示', async ({ authenticatedUser: page }) => {
    // 验证有持仓数据
    const rows = page.locator('tbody tr');
    expect(await rows.count()).toBeGreaterThan(0);
    
    // 验证每个持仓都有盈亏显示
    await aiAssert(page, '持仓表格中显示了盈亏金额和盈亏率');
  });

  test('平仓功能 - 正常流程', async ({ authenticatedUser: page }) => {
    // 找到第一个平仓按钮
    const closeButton = page.locator('text=平仓').first();
    
    // 点击平仓
    page.once('dialog', dialog => {
      expect(dialog.message()).toContain('平仓');
      dialog.accept();
    });
    
    await midscene(page, '点击第一个持仓的平仓按钮');
  });

  test('统计卡片数据真实性', async ({ authenticatedUser: page }) => {
    // 持仓总数
    const totalPositions = await aiQuery(page, '获取持仓总数的数值');
    expect(totalPositions).toBeTruthy();
    
    // 总盈亏
    const totalPnl = await aiQuery(page, '获取总盈亏的数值');
    expect(totalPnl).toBeTruthy();
    
    // 保证金占用
    const margin = await aiQuery(page, '获取保证金占用的数值');
    expect(margin).toBeTruthy();
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

  test('方向显示正确性 - 多/空', async ({ authenticatedUser: page }) => {
    // 验证有方向列
    await expect(page.locator('text=方向')).toBeVisible();
    
    // 验证有做多或做空标识
    await aiAssert(page, '持仓表格中显示了做多或做空的方向标识');
  });
});
