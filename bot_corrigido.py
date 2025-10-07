#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOT DE TRADING CORRIGIDO - VERSÃO FUNCIONAL
✅ Corrige o problema de não abrir trades
✅ Implementa função de abertura de posições
✅ Ativa o trading real
"""

import os
import sys
import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import ccxt
import requests
from dataclasses import dataclass

# Configurações básicas
class TradingConfig:
    MIN_BALANCE = 10.0
    POSITION_SIZE_PCT = 0.01  # 1% do saldo
    MAX_POSITIONS = 3
    COOLDOWN_MINUTES = 30

class Logger:
    def __init__(self):
        self.logger = self
    
    def info(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def warning(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ {msg}")
    
    def error(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {msg}")
    
    def debug(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 {msg}")

logger = Logger()

class SimpleRiskManager:
    def __init__(self):
        self.daily_pnl = 0.0
        self.consecutive_losses = 0
        self.error_count = 0
        self.last_reset = datetime.now().date()
    
    def can_trade(self) -> Tuple[bool, str]:
        """Verifica se pode operar"""
        # Reset diário
        if datetime.now().date() != self.last_reset:
            self.daily_pnl = 0.0
            self.consecutive_losses = 0
            self.error_count = 0
            self.last_reset = datetime.now().date()
        
        # Verificações básicas
        if self.daily_pnl <= -0.05:  # -5% de perda diária
            return False, f"Daily loss limit: {self.daily_pnl*100:.1f}%"
        
        if self.consecutive_losses >= 3:
            return False, f"Consecutive losses: {self.consecutive_losses}"
        
        if self.error_count >= 10:
            return False, "Too many errors"
        
        return True, "OK"

class SimpleAnalyzer:
    def __init__(self):
        pass
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcula RSI de forma simples"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calcula EMA"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def analyze_symbol(self, symbol: str, ohlcv_data: Dict) -> Optional[Dict]:
        """Análise simples de símbolo"""
        try:
            # Usar dados de 15m para análise
            if '15m' not in ohlcv_data:
                return None
            
            df = ohlcv_data['15m']
            if len(df) < 20:
                return None
            
            closes = df['close'].tolist()
            highs = df['high'].tolist()
            lows = df['low'].tolist()
            volumes = df['volume'].tolist()
            
            # Calcular indicadores
            rsi = self.calculate_rsi(closes)
            ema_20 = self.calculate_ema(closes, 20)
            ema_50 = self.calculate_ema(closes, 50)
            
            current_price = closes[-1]
            volume_avg = sum(volumes[-10:]) / 10
            current_volume = volumes[-1]
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            
            # Lógica de sinal simples
            signal = 'NEUTRAL'
            score = 0
            confidence = 0
            
            # Condições para LONG
            if (rsi < 70 and rsi > 30 and  # RSI não sobrecomprado/sobrevendido
                current_price > ema_20 and  # Preço acima da EMA 20
                ema_20 > ema_50 and  # Tendência de alta
                volume_ratio > 1.2):  # Volume acima da média
                
                signal = 'LONG'
                score = min(5.0, (70 - rsi) / 10 + 2)
                confidence = min(0.9, volume_ratio / 2)
            
            # Condições para SHORT
            elif (rsi > 30 and rsi < 70 and  # RSI não sobrecomprado/sobrevendido
                  current_price < ema_20 and  # Preço abaixo da EMA 20
                  ema_20 < ema_50 and  # Tendência de baixa
                  volume_ratio > 1.2):  # Volume acima da média
                
                signal = 'SHORT'
                score = min(5.0, (rsi - 30) / 10 + 2)
                confidence = min(0.9, volume_ratio / 2)
            
            # Retornar apenas sinais válidos
            if signal != 'NEUTRAL' and score >= 3.0 and confidence >= 0.6:
                return {
                    'signal': signal,
                    'score': score,
                    'confidence': confidence,
                    'rsi': rsi,
                    'price': current_price,
                    'volume_ratio': volume_ratio,
                    'ema_20': ema_20,
                    'ema_50': ema_50
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Analysis error {symbol}: {e}")
            return None

class WorkingTradingBot:
    def __init__(self, testnet: bool = True):
        logger.info("🚀 Initializing WORKING Trading Bot...")
        
        # Componentes
        self.risk_manager = SimpleRiskManager()
        self.analyzer = SimpleAnalyzer()
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT'
        ]
        self.timeframes = ['15m', '1h']
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = TradingConfig.COOLDOWN_MINUTES * 60
        
        logger.info(f"✅ Bot initialized - {len(self.symbols)} symbols")

    def _setup_exchange(self):
        """Configura exchange"""
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("❌ API keys not configured")
        
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'sandbox': self.testnet,
        })
        
        logger.info("✅ Exchange configured")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> Optional[pd.DataFrame]:
        """Busca dados OHLCV"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if len(ohlcv) < 20:
                return None
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
            return None

    def open_position_simple(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição de forma simples e segura"""
        try:
            # Verificar se pode operar
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                logger.warning(f"⏸️ Cannot trade: {reason}")
                return False
            
            # Verificar se já tem posição ativa
            if symbol in self.active_positions:
                logger.debug(f"⏸️ Position already active: {symbol}")
                return False
            
            # Verificar cooldown
            current_time = time.time()
            if symbol in self.symbol_cooldown:
                if current_time - self.symbol_cooldown[symbol] < self.min_cooldown:
                    logger.debug(f"⏸️ Cooldown active: {symbol}")
                    return False
            
            # Calcular quantidade baseada no saldo
            balance = self.exchange.fetch_balance()
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            
            if usdt_balance < TradingConfig.MIN_BALANCE:
                logger.warning(f"❌ Insufficient balance: ${usdt_balance:.2f}")
                return False
            
            # Quantidade conservadora
            quantity = (usdt_balance * TradingConfig.POSITION_SIZE_PCT) / signal_info['price']
            
            # Executar ordem
            signal = signal_info['signal']
            if signal == 'LONG':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.info(f"✅ Position opened: {symbol} {signal} | Order: {order.get('id')}")
            
            # Registrar posição ativa
            self.active_positions[symbol] = {
                'symbol': symbol,
                'side': signal,
                'entry_price': signal_info['price'],
                'quantity': quantity,
                'order_id': order.get('id'),
                'timestamp': datetime.now()
            }
            
            # Ativar cooldown
            self.symbol_cooldown[symbol] = current_time
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Position open error {symbol}: {e}")
            self.risk_manager.error_count += 1
            return False

    def analyze_symbol_working(self, symbol: str) -> Optional[Dict]:
        """Análise funcional de símbolo"""
        try:
            # Buscar dados para todos os timeframes
            ohlcv_data = {}
            for timeframe in self.timeframes:
                df = self.fetch_ohlcv(symbol, timeframe, 50)
                if df is not None:
                    ohlcv_data[timeframe] = df
            
            if len(ohlcv_data) < 1:
                return None
            
            # Análise
            result = self.analyzer.analyze_symbol(symbol, ohlcv_data)
            return result
            
        except Exception as e:
            logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def run_working_cycle(self) -> int:
        """Ciclo de trading funcional"""
        positions_opened = 0
        
        try:
            # Símbolos disponíveis para análise
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            logger.info(f"🔍 Analyzing {len(available_symbols)} symbols...")
            
            # Analisar símbolos sequencialmente
            for symbol in available_symbols[:5]:  # Limitar a 5 por ciclo
                try:
                    result = self.analyze_symbol_working(symbol)
                    
                    if result:
                        logger.info(f"🎯 VALID SIGNAL: {symbol} {result['signal']} "
                                 f"(Score: {result['score']:.1f}, RSI: {result['rsi']:.1f})")
                        
                        # Abrir posição real
                        success = self.open_position_simple(symbol, result)
                        if success:
                            positions_opened += 1
                        
                except Exception as e:
                    logger.debug(f"Symbol analysis error {symbol}: {e}")
                    continue
            
            logger.info(f"📊 Cycle complete: {len(available_symbols)} analyzed, {positions_opened} positions opened")
            
            return positions_opened
            
        except Exception as e:
            logger.error(f"❌ Cycle error: {e}")
            return 0

    def run_continuous_analysis(self):
        """Loop contínuo de análise e trading"""
        logger.info(f"\n{'='*60}")
        logger.info("🚀 WORKING TRADING BOT - ACTIVE MODE")
        logger.info("✅ Fixed technical indicators")
        logger.info("✅ Reliable symbols only") 
        logger.info("✅ Conservative signal criteria")
        logger.info("✅ TRADING ENABLED")
        logger.info(f"{'='*60}\n")
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                start_time = time.time()
                
                logger.info(f"\n[🔄 CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                
                # Executar análise e trading
                positions_opened = self.run_working_cycle()
                
                if positions_opened > 0:
                    logger.info(f"🎯 Opened {positions_opened} positions this cycle")
                else:
                    logger.info("⏸️ No positions opened this cycle")
                
                # Timing do ciclo
                cycle_duration = time.time() - start_time
                sleep_time = max(30, 120 - cycle_duration)  # 2 minutos entre ciclos
                
                logger.info(f"⏱️ Next analysis in {sleep_time:.0f}s")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot error: {e}")

def main():
    try:
        # Verificar variáveis de ambiente
        required_vars = ['BYBIT_API_KEY', 'BYBIT_API_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing: {', '.join(missing_vars)}")
            return
        
        print(f"\n{'='*60}")
        print(f"🚀 WORKING TRADING BOT - FIXED VERSION")
        print(f"{'='*60}")
        print(f"✅ Fixed technical indicators")
        print(f"✅ Reliable RSI calculation") 
        print(f"✅ Conservative analysis")
        print(f"✅ TRADING ENABLED")
        print(f"{'='*60}")
        
        # Iniciar bot
        bot = WorkingTradingBot(testnet=True)
        bot.run_continuous_analysis()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        print(f"❌ Bot crashed: {e}")

if __name__ == '__main__':
    main()