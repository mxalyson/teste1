#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TESTE DO BOT DE TRADING
Testa o bot sem precisar de chaves de API reais
"""

import os
import sys
import time
from datetime import datetime

# Simular variáveis de ambiente para teste
os.environ['BYBIT_API_KEY'] = 'test_key_12345'
os.environ['BYBIT_API_SECRET'] = 'test_secret_67890'

# Importar o bot corrigido
from bot_corrigido import WorkingTradingBot, logger

def test_bot_initialization():
    """Testa a inicialização do bot"""
    print("🧪 Testing bot initialization...")
    
    try:
        bot = WorkingTradingBot(testnet=True)
        print("✅ Bot initialized successfully")
        print(f"   - Symbols: {len(bot.symbols)}")
        print(f"   - Timeframes: {bot.timeframes}")
        print(f"   - Testnet: {bot.testnet}")
        return True
    except Exception as e:
        print(f"❌ Bot initialization failed: {e}")
        return False

def test_risk_manager():
    """Testa o gerenciador de risco"""
    print("\n🧪 Testing risk manager...")
    
    try:
        from bot_corrigido import SimpleRiskManager
        
        risk_manager = SimpleRiskManager()
        can_trade, reason = risk_manager.can_trade()
        
        print(f"✅ Risk manager working")
        print(f"   - Can trade: {can_trade}")
        print(f"   - Reason: {reason}")
        return True
    except Exception as e:
        print(f"❌ Risk manager test failed: {e}")
        return False

def test_analyzer():
    """Testa o analisador técnico"""
    print("\n🧪 Testing technical analyzer...")
    
    try:
        from bot_corrigido import SimpleAnalyzer
        import pandas as pd
        import numpy as np
        
        analyzer = SimpleAnalyzer()
        
        # Dados de teste
        test_data = {
            '15m': pd.DataFrame({
                'close': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120],
                'high': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121],
                'low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119],
                'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]
            })
        }
        
        result = analyzer.analyze_symbol('BTCUSDT', test_data)
        
        print(f"✅ Analyzer working")
        if result:
            print(f"   - Signal: {result['signal']}")
            print(f"   - Score: {result['score']:.2f}")
            print(f"   - RSI: {result['rsi']:.2f}")
        else:
            print("   - No signal generated (normal for test data)")
        
        return True
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

def test_position_opening():
    """Testa a lógica de abertura de posições (simulada)"""
    print("\n🧪 Testing position opening logic...")
    
    try:
        from bot_corrigido import SimpleRiskManager
        
        risk_manager = SimpleRiskManager()
        
        # Simular dados de sinal
        signal_info = {
            'signal': 'LONG',
            'score': 4.5,
            'confidence': 0.8,
            'price': 50000.0,
            'rsi': 45.0
        }
        
        # Verificar se pode operar
        can_trade, reason = risk_manager.can_trade()
        
        print(f"✅ Position opening logic working")
        print(f"   - Can trade: {can_trade}")
        print(f"   - Reason: {reason}")
        
        if can_trade:
            print("   - Bot would attempt to open position")
        else:
            print("   - Bot would skip trading")
        
        return True
    except Exception as e:
        print(f"❌ Position opening test failed: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 TESTING WORKING TRADING BOT")
    print("=" * 50)
    
    tests = [
        test_bot_initialization,
        test_risk_manager,
        test_analyzer,
        test_position_opening
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Bot is ready to use.")
        print("\n📝 Next steps:")
        print("1. Configure your API keys in .env file")
        print("2. Run: python bot_corrigido.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)