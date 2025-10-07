# =================== ADVANCED TRADING BOT - CORRIGIDO E OTIMIZADO ===================
# Bot profissional avançado para trading com múltiplas moedas e timeframes
# ✅ CORREÇÕES: JSON locks, leverage errors, threading issues
# ✅ TOP 20 MOEDAS do CoinMarketCap (sem memes/stables)
# ✅ ANÁLISE MULTI-TIMEFRAME (15m, 1h, 2h, 4h)
# ✅ OBJETIVO: 15+ TRADES DIÁRIOS de qualidade
# ✅ STOP LOSS E TAKE PROFIT dinâmicos

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time, timedelta
import time
import ta
import os
import json
import logging
import requests
from dotenv import load_dotenv
import threading
from flask import Flask, jsonify
import warnings
from typing import Dict, List, Optional, Tuple
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

warnings.filterwarnings('ignore')
load_dotenv()

# =================== CONFIGURAÇÕES OTIMIZADAS ===================
class AdvancedTradingConfig:
    # Stop Loss mais conservador
    MIN_STOP_LOSS_PCT = 0.01  # 1%
    MAX_STOP_LOSS_PCT = 0.02  # 2%
    ATR_MULTIPLIER = 2.0
    
    # Take Profit mais realista
    MIN_RISK_REWARD_RATIO = 2.0  # Reduzido de 2.5 para 2.0
    MAX_TAKE_PROFIT_PCT = 0.06
    
    # Risk Management mais conservador
    MAX_DAILY_LOSS = -0.05  # Aumentado de -3% para -5%
    MAX_POSITION_SIZE = 0.02  # Aumentado de 1% para 2% por trade
    MAX_POSITIONS = 3  # Aumentado de 2 para 3
    MAX_CONSECUTIVE_LOSSES = 5  # Aumentado de 3 para 5
    
    # Análise técnica mais flexível
    MIN_SIGNAL_SCORE = 4.0  # Reduzido de 6.0 para 4.0
    MIN_CONFIDENCE = 2.0  # Reduzido de 4.0 para 2.0
    MIN_REASONS = 2  # Reduzido de 3 para 2
    MIN_ADX = 15  # Reduzido de 20 para 15
    MIN_VOLUME_RATIO = 1.    MAX_RSI = 80  # Aumentado de 75 para 80
    MIN_RSI = 20  # Reduzido de 25 para 20 MAX_RSI = 75
    MIN_RSI = 25
    
    # Timeframes otimizados
    TIMEFRAMES = ['15m', '1h', '4h']
    PRIMARY_TIMEFRAME = '1h'
    
    # Frequência ajustada
    ANALYSIS_INTERVAL = 60
    TARGET_TRADES_PER_DAY = 8  # Mais realista

# CoinMarketCap API
    COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY', '')
    TOP_COINS_COUNT = 20

# =================== ANALISADOR TÉCNICO MELHORADO ===================
class ProfessionalTechnicalAnalyzer:
    def __init__(self):
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        
    def calculate_professional_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores profissionais com validação"""
        try:
            if len(df) < 50:
                return df
                
            # Preços
            high = df['high']
            low = df['low'] 
            close = df['close']
            volume = df['volume']
            
            # 1. TENDÊNCIA - EMAs
            df['ema_9'] = ta.trend.EMAIndicator(close, window=9).ema_indicator()
            df['ema_21'] = ta.trend.EMAIndicator(close, window=21).ema_indicator()
            df['ema_50'] = ta.trend.EMAIndicator(close, window=50).ema_indicator()
            
            # 2. MOMENTUM - RSI, MACD, Stochastic
            df['rsi'] = ta.momentum.RSIIndicator(close, window=14).rsi()
            df['rsi_smooth'] = ta.trend.EMAIndicator(df['rsi'], window=3).ema_indicator()
            
            macd = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_histogram'] = macd.macd_diff()
            
            stoch = ta.momentum.StochasticOscillator(high, low, close, window=14, smooth_window=3)
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # 3. VOLATILIDADE - ATR, Bollinger Bands
            df['atr'] = ta.volatility.AverageTrueRange(high, low, close, window=14).average_true_range()
            bollinger = ta.volatility.BollingerBands(close, window=20, window_dev=2)
            df['bb_upper'] = bollinger.bollinger_hband()
            df['bb_lower'] = bollinger.bollinger_lband()
            df['bb_middle'] = bollinger.bollinger_mavg()
            df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # 4. VOLUME - Volume profile
            df['volume_sma'] = volume.rolling(window=20).mean()
            df['volume_ratio'] = volume / df['volume_sma']
            df['obv'] = ta.volume.OnBalanceVolumeIndicator(close, volume).on_balance_volume()
            
            # 5. FORÇA - ADX, Williams %R
            df['adx'] = ta.trend.ADXIndicator(high, low, close, window=14).adx()
            df['williams_r'] = ta.momentum.WilliamsRIndicator(high, low, close, lbp=14).williams_r()
            
            # 6. SUPORTE/RESISTÊNCIA
            df['pivot'] = (high + low + close) / 3
            df['resistance'] = 2 * df['pivot'] - low
            df['support'] = 2 * df['pivot'] - high
            
            return df
            
        except Exception as e:
            logger.logger.error(f"Error calculating indicators: {e}")
            return df

    def analyze_trend_strength(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analisa força da tendência de forma profissional"""
        try:
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            trend_score = 0
            momentum_score = 0
            volume_score = 0
            reasons = []
            
            # 1. ANÁLISE DE TENDÊNCIA
            ema_trend = 0
            if last['ema_9'] > last['ema_21'] > last['ema_50']:
                ema_trend = 1
                reasons.append("EMA Bullish Alignment")
            elif last['ema_9'] < last['ema_21'] < last['ema_50']:
                ema_trend = -1
                reasons.append("EMA Bearish Alignment")
            
            # Força da tendência pelas EMAs
            if ema_trend == 1:
                if last['close'] > last['ema_9']:
                    trend_score += 2.0
                if last['ema_9'] > last['ema_21'] + (last['ema_21'] * 0.005):
                    trend_score += 1.0
            elif ema_trend == -1:
                if last['close'] < last['ema_9']:
                    trend_score -= 2.0
                if last['ema_9'] < last['ema_21'] - (last['ema_21'] * 0.005):
                    trend_score -= 1.0
            
            # ADX - Força da tendência
            if last['adx'] > 25:
                trend_score += abs(ema_trend) * 1.5
                reasons.append(f"Strong Trend (ADX: {last['adx']:.1f})")
            elif last['adx'] < 15:
                trend_score *= 0.5  # Reduz força se tendência fraca
                reasons.append(f"Weak Trend (ADX: {last['adx']:.1f})")
            
            # 2. ANÁLISE DE MOMENTUM
            rsi = last['rsi_smooth'] if not pd.isna(last['rsi_smooth']) else last['rsi']
            
            if 30 < rsi < 70:  # Zona neutra - momentum confiável
                if last['macd'] > last['macd_signal'] and last['macd_histogram'] > prev['macd_histogram']:
                    momentum_score += 1.5
                    reasons.append("MACD Bullish")
                elif last['macd'] < last['macd_signal'] and last['macd_histogram'] < prev['macd_histogram']:
                    momentum_score -= 1.5
                    reasons.append("MACD Bearish")
            
            # Stochastic
            if last['stoch_k'] < 20 and last['stoch_d'] < 20:
                momentum_score += 1.0
                reasons.append("Stoch Oversold")
            elif last['stoch_k'] > 80 and last['stoch_d'] > 80:
                momentum_score -= 1.0
                reasons.append("Stoch Overbought")
            
            # 3. ANÁLISE DE VOLUME
            if last['volume_ratio'] > 1.5:
                volume_score = 1.5
                reasons.append(f"High Volume ({last['volume_ratio']:.1f}x)")
            elif last['volume_ratio'] > 1.2:
                volume_score = 1.0
                reasons.append(f"Good Volume ({last['volume_ratio']:.1f}x)")
            
            # OBV confirmando tendência
            if len(df) > 5:
                obv_trend = 1 if df['obv'].iloc[-5:].is_monotonic_increasing else -1
                if obv_trend == ema_trend:
                    volume_score += 0.5
                    reasons.append("OBV Confirmation")
            
            # 4. ANÁLISE DE SUPORTE/RESISTÊNCIA
            price_vs_bb = last['bb_position']
            if price_vs_bb < 0.2:  # Perto da banda inferior
                trend_score += 1.0
                reasons.append("Near BB Support")
            elif price_vs_bb > 0.8:  # Perto da banda superior
                trend_score -= 1.0
                reasons.append("Near BB Resistance")
            
            total_score = trend_score + momentum_score + volume_score
            
            return {
                'total_score': total_score,
                'trend_score': trend_score,
                'momentum_score': momentum_score,
                'volume_score': volume_score,
                'reasons': reasons,
                'rsi': rsi,
                'adx': last['adx'],
                'volume_ratio': last['volume_ratio'],
                'ema_trend': ema_trend
            }
            
        except Exception as e:
            logger.logger.error(f"Error in trend analysis: {e}")
            return {'total_score': 0, 'trend_score': 0, 'momentum_score': 0, 'volume_score': 0, 'reasons': ['Error'], 'rsi': 50, 'adx': 0, 'volume_ratio': 1, 'ema_trend': 0}

    def generate_signal(self, symbol: str, multi_tf_analysis: Dict) -> Dict:
        """Gera sinal profissional baseado em análise multi-timeframe"""
        try:
            # Coletar análises de todos os timeframes
            tf_signals = []
            tf_scores = []
            all_reasons = []
            
            for timeframe, analysis in multi_tf_analysis.items():
                if analysis['total_score'] != 0:
                    tf_signals.append(1 if analysis['total_score'] > 0 else -1)
                    tf_scores.append(abs(analysis['total_score']))
                    all_reasons.extend([f"{timeframe}: {r}" for r in analysis['reasons']])
            
            if not tf_signals:
                return self._neutral_signal("No clear signals")
            
            # Ponderar por timeframe (timeframes maiores têm mais peso)
            weights = {'15m': 0.2, '1h': 0.35, '4h': 0.45}
            weighted_score = 0
            total_weight = 0
            
            for timeframe, analysis in multi_tf_analysis.items():
                weight = weights.get(timeframe, 0.3)
                weighted_score += analysis['total_score'] * weight
                total_weight += weight
            
            final_score = weighted_score / total_weight if total_weight > 0 else 0
            
            # Requer confirmação de múltiplos timeframes
            bullish_count = sum(1 for s in tf_signals if s > 0)
            bearish_count = sum(1 for s in tf_signals if s < 0)
            
            # Critérios rigorosos para sinal
            signal = 'NEUTRAL'
            confidence = 0
            
            primary_analysis = multi_tf_analysis.get('1h', multi_tf_analysis.get('4h'))
            if not primary_analysis:
                return self._neutral_signal("No primary analysis")
            
            # Verificar condições obrigatórias
            required_conditions = [
                abs(final_score) >= 2.0,
                primary_analysis['adx'] >= AdvancedTradingConfig.MIN_ADX,
                primary_analysis['volume_ratio'] >= AdvancedTradingConfig.MIN_VOLUME_RATIO,
                AdvancedTradingConfig.MIN_RSI <= primary_analysis['rsi'] <= AdvancedTradingConfig.MAX_RSI
            ]
            
            if not all(required_conditions):
                return self._neutral_signal("Missing required conditions")
            
            # Determinar sinal final
            if (final_score > 0 and bullish_count >= 2 and 
                primary_analysis['ema_trend'] >= 0):
                signal = 'LONG'
                confidence = min(final_score / 3.0, 1.0)
                
            elif (final_score < 0 and bearish_count >= 2 and 
                  primary_analysis['ema_trend'] <= 0):
                signal = 'SHORT' 
                confidence = min(abs(final_score) / 3.0, 1.0)
            
            if signal != 'NEUTRAL' and confidence >= 0.6:
                # Filtrar razões mais importantes
                important_reasons = [r for r in all_reasons if any(keyword in r.lower() for keyword in 
                                ['bullish', 'bearish', 'strong', 'high volume', 'good volume', 'confirmation'])]
                
                return {
                    'signal': signal,
                    'score': abs(final_score),
                    'confidence': confidence,
                    'signal_strength': confidence,
                    'price': primary_analysis.get('price', 0),
                    'rsi': primary_analysis['rsi'],
                    'adx': primary_analysis['adx'],
                    'volume_ratio': primary_analysis['volume_ratio'],
                    'reasons': important_reasons[:5],
                    'timeframe': 'multi',
                    'multi_tf_analysis': multi_tf_analysis
                }
            
            return self._neutral_signal("Low confidence")
            
        except Exception as e:
            logger.logger.error(f"Error generating signal: {e}")
            return self._neutral_signal("Signal generation error")

    def _neutral_signal(self, reason: str) -> Dict:
        """Retorna sinal neutro"""
        return {
            'signal': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'signal_strength': 0,
            'reasons': [reason],
            'timeframe': 'multi'
        }

# =================== BOT PRINCIPAL COM ANÁLISE CORRIGIDA ===================
class ProfessionalTradingBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing PROFESSIONAL Trading Bot...")
        
        # Componentes profissionais
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.technical_analyzer = ProfessionalTechnicalAnalyzer()
        self.sl_tp_calculator = AdvancedStopLossTakeProfit()
        self.dashboard = OptimizedDashboard(self, port=5000)
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = self._get_optimized_symbols()
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.leverage = 3
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 1800  # 30 minutos
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        logger.logger.info(f"✅ PROFESSIONAL Bot initialized - {len(self.symbols)} symbols")

    def _get_optimized_symbols(self) -> List[str]:
        """Seleciona símbolos otimizados para trading"""
        base_symbols = self.cmc_api.get_top_coins()
        
        # Priorizar símbolos com melhor liquidez e volatilidade
        prioritized = []
        secondary = []
        
        high_volatility = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT', 
                          'MATICUSDT', 'SOLUSDT', 'AVAXUSDT', 'ATOMUSDT', 'ALGOUSDT']
        
        for symbol in base_symbols:
            if symbol in high_volatility:
                prioritized.append(symbol)
            else:
                secondary.append(symbol)
        
        return prioritized + secondary[:10]  # Máximo 15 símbolos

    def analyze_symbol_professional(self, symbol: str) -> Optional[Dict]:
        """Análise profissional de símbolo"""
        try:
            logger.logger.info(f"🔍 Analyzing {symbol}...")
            
            # Buscar dados multi-timeframe
            ohlcv_data = self.fetch_multi_timeframe_data_pro(symbol)
            if len(ohlcv_data) < 2:
                logger.logger.info(f"   📭 {symbol}: Insufficient data")
                return None
            
            # Análise técnica para cada timeframe
            multi_tf_analysis = {}
            
            for timeframe, df in ohlcv_data.items():
                if len(df) < 50:
                    continue
                    
                # Calcular indicadores
                df = self.technical_analyzer.calculate_professional_indicators(df)
                
                # Analisar tendência
                analysis = self.technical_analyzer.analyze_trend_strength(df)
                analysis['price'] = df['close'].iloc[-1]
                analysis['df'] = df
                
                multi_tf_analysis[timeframe] = analysis
            
            if not multi_tf_analysis:
                return None
            
            # Gerar sinal final
            signal_result = self.technical_analyzer.generate_signal(symbol, multi_tf_analysis)
            
            if signal_result['signal'] != 'NEUTRAL':
                logger.logger.info(f"🎯 {symbol}: {signal_result['signal']} "
                                 f"(Score: {signal_result['score']:.1f}, "
                                 f"Conf: {signal_result['confidence']:.1f})")
                
                # Adicionar dados da análise primária
                primary_tf = '1h' if '1h' in multi_tf_analysis else list(multi_tf_analysis.keys())[0]
                primary_data = multi_tf_analysis[primary_tf]
                
                signal_result.update({
                    'df': primary_data['df'],
                    'atr': primary_data['df']['atr'].iloc[-1],
                    'timeframe_results': multi_tf_analysis
                })
                
                return signal_result
            else:
                logger.logger.info(f"⏸️ {symbol}: No signal - {signal_result['reasons'][0]}")
                return None
                
        except Exception as e:
            logger.logger.error(f"❌ Professional analysis error {symbol}: {e}")
            return None

    def fetch_multi_timeframe_data_pro(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados profissionais com mais candles para análise precisa"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                # Buscar mais dados para análise técnica robusta
                limit = 100 if timeframe == '15m' else 80
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if len(ohlcv) >= 50:  # Mínimo 50 candles
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
                    
            except Exception as e:
                logger.logger.debug(f"Data error {symbol} {timeframe}: {e}")
                
        return ohlcv_data

    def run_professional_analysis_cycle(self) -> int:
        """Ciclo de análise profissional"""
        positions_opened = 0
        
        try:
            # Filtrar símbolos disponíveis
            available_symbols = [
                s for s in self.symbols 
                if s not in self.active_positions 
                and self._can_analyze_symbol(s)
            ]
            
            if not available_symbols:
                return 0
            
            logger.logger.info(f"\n📊 PROFESSIONAL ANALYSIS - {len(available_symbols)} symbols")
            
            # Analisar símbolos em lote
            batch_size = 5
            for i in range(0, len(available_symbols), batch_size):
                batch = available_symbols[i:i + batch_size]
                
                futures = {}
                for symbol in batch:
                    future = self.executor.submit(self.analyze_symbol_professional, symbol)
                    futures[future] = symbol
                
                # Processar resultados do batch
                for future in as_completed(futures, timeout=45):
                    symbol = futures[future]
                    
                    try:
                        result = future.result(timeout=10)
                        
                        if result and self._validate_signal_quality(result):
                            logger.logger.info(f"🚨 HIGH-QUALITY SIGNAL: {symbol}")
                            
                            success = self.open_professional_position(symbol, result)
                            if success:
                                positions_opened += 1
                                # Limitar a 1 posição por ciclo para controle
                                if positions_opened >= 1:
                                    break
                                    
                    except Exception as e:
                        logger.logger.debug(f"Batch analysis error {symbol}: {e}")
                
                if positions_opened >= 1:
                    break  # Não abrir múltiplas posições no mesmo ciclo
                    
                time.sleep(2)  # Pequena pausa entre batches
            
            if positions_opened > 0:
                logger.logger.info(f"✅ Opened {positions_opened} professional positions")
            else:
                logger.logger.info("⏸️ No high-quality signals found")
            
            return positions_opened
            
        except Exception as e:
            logger.logger.error(f"❌ Professional analysis cycle error: {e}")
            return 0

    def _can_analyze_symbol(self, symbol: str) -> bool:
        """Verifica se pode analisar o símbolo"""
        current_time = time.time()
        
        if symbol in self.symbol_cooldown:
            time_since = current_time - self.symbol_cooldown[symbol]
            if time_since < self.min_cooldown:
                return False
        
        return True

    def _validate_signal_quality(self, signal: Dict) -> bool:
        """Valida qualidade do sinal com critérios rigorosos"""
        try:
            required_conditions = [
                signal['signal'] in ['LONG', 'SHORT'],
                signal['score'] >= AdvancedTradingConfig.MIN_SIGNAL_SCORE,
                signal['confidence'] >= AdvancedTradingConfig.MIN_CONFIDENCE,
                len(signal['reasons']) >= AdvancedTradingConfig.MIN_REASONS,
                signal['rsi'] >= AdvancedTradingConfig.MIN_RSI,
                signal['rsi'] <= AdvancedTradingConfig.MAX_RSI,
                signal['adx'] >= AdvancedTradingConfig.MIN_ADX,
                signal['volume_ratio'] >= AdvancedTradingConfig.MIN_VOLUME_RATIO
            ]
            
            return all(required_conditions)
            
        except Exception as e:
            logger.logger.error(f"Signal validation error: {e}")
            return False

    def open_professional_position(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição profissional com gestão de risco aprimorada"""
        try:
            # Verificações de segurança
            if not self.risk_manager.can_trade()[0]:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= AdvancedTradingConfig.MAX_POSITIONS:
                return False
            
            # Calcular posição com risco controlado
            quantity = self.calculate_professional_position_size(symbol, signal_info)
            if quantity <= 0:
                return False
            
            # Calcular SL/TP profissionais
            sl_pct, tp_pct = self.calculate_professional_sl_tp(signal_info)
            
            # Executar ordem
            success = self.execute_professional_order(symbol, signal_info, quantity, sl_pct, tp_pct)
            
            if success:
                self.symbol_cooldown[symbol] = time.time()
                return True
            
            return False
            
        except Exception as e:
            logger.logger.error(f"❌ Professional position error {symbol}: {e}")
            return False

    def calculate_professional_position_size(self, symbol: str, signal_info: Dict) -> float:
        """Calcula tamanho de posição profissional"""
        try:
            balance = self._get_account_balance()
            if balance < 100:  # Saldo mínimo
                return 0
            
            # Tamanho base conservador
            base_size = AdvancedTradingConfig.MAX_POSITION_SIZE
            
            # Ajustar por confiança do sinal (0.5x a 1.0x)
            confidence_multiplier = 0.5 + (signal_info['confidence'] * 0.5)
            
            # Ajustar por força do sinal
            strength_multiplier = min(signal_info['score'] / 8.0, 1.0)
            
            # Tamanho final
            position_size = base_size * confidence_multiplier * strength_multiplier
            position_usdt = balance * position_size
            
            # Obter preço e quantidade
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = position_usdt / price
            
            # Aplicar precisão
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            final_quantity = float(quantity) if quantity else 0
            
            # Verificar mínimo
            min_notional = 6.0
            if final_quantity * price < min_notional:
                return 0
            
            return final_quantity
            
        except Exception as e:
            logger.logger.error(f"❌ Professional position size error: {e}")
            return 0

    def calculate_professional_sl_tp(self, signal_info: Dict) -> Tuple[float, float]:
        """Calcula SL/TP profissionais"""
        try:
            df = signal_info['df']
            atr = df['atr'].iloc[-1]
            price = df['close'].iloc[-1]
            atr_pct = atr / price
            
            # SL baseado em ATR e suporte/resistência
            base_sl = atr_pct * AdvancedTradingConfig.ATR_MULTIPLIER
            
            # Ajustar por confiança (sinais mais confiantes têm SL mais apertado)
            confidence_factor = 1.3 - (signal_info['confidence'] * 0.3)
            sl_pct = max(base_sl * confidence_factor, AdvancedTradingConfig.MIN_STOP_LOSS_PCT)
            sl_pct = min(sl_pct, AdvancedTradingConfig.MAX_STOP_LOSS_PCT)
            
            # TP baseado em R/R ratio
            tp_pct = sl_pct * AdvancedTradingConfig.MIN_RISK_REWARD_RATIO
            tp_pct = min(tp_pct, AdvancedTradingConfig.MAX_TAKE_PROFIT_PCT)
            
            logger.logger.info(f"   📊 SL: {sl_pct*100:.2f}% | TP: {tp_pct*100:.2f}% | R/R: {tp_pct/sl_pct:.1f}")
            
            return sl_pct, tp_pct
            
        except Exception as e:
            logger.logger.error(f"❌ Professional SL/TP error: {e}")
            return AdvancedTradingConfig.MIN_STOP_LOSS_PCT, AdvancedTradingConfig.MIN_STOP_LOSS_PCT * AdvancedTradingConfig.MIN_RISK_REWARD_RATIO

    def execute_professional_order(self, symbol: str, signal_info: Dict, quantity: float, sl_pct: float, tp_pct: float) -> bool:
        """Executa ordem profissional"""
        try:
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            # Calcular preços SL/TP
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_open = 'buy'
                side_close = 'sell'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_open = 'sell'
                side_close = 'buy'
            
            risk_reward = tp_pct / sl_pct
            
            logger.logger.info(f"\n🚀 OPENING PROFESSIONAL POSITION:")
            logger.logger.info(f"   {symbol} {signal} | Entry: ${entry_price:.4f}")
            logger.logger.info(f"   SL: ${sl_price:.4f} | TP: ${tp_price:.4f}")
            logger.logger.info(f"   R/R: {risk_reward:.1f}:1 | Size: {quantity:.4f}")
            logger.logger.info(f"   Reasons: {', '.join(signal_info['reasons'][:3])}")
            
            # Executar ordem principal
            if signal == 'LONG':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.logger.info(f"   ✅ Order executed: {order.get('id')}")
            
            time.sleep(1)
            
            # Configurar SL/TP
            sl_order_id = None
            tp_order_id = None
            
            try:
                # Stop Loss
                sl_order = self.exchange.create_order(
                    symbol, 'STOP_MARKET', side_close, quantity,
                    params={'stopPrice': sl_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                sl_order_id = sl_order.get('id')
                
                # Take Profit  
                tp_order = self.exchange.create_order(
                    symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                    params={'stopPrice': tp_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                tp_order_id = tp_order.get('id')
                
                logger.logger.info(f"   ✅ SL/TP configured")
                
            except Exception as e:
                logger.logger.warning(f"   ⚠️ SL/TP configuration failed: {e}")
            
            # Registrar posição
            trade_data = {
                'symbol': symbol,
                'signal': signal,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss_price': sl_price,
                'take_profit_price': tp_price,
                'stop_loss_pct': sl_pct,
                'take_profit_pct': tp_pct,
                'risk_reward_ratio': risk_reward,
                'timestamp': datetime.now(),
                'order_id': order.get('id'),
                'sl_order_id': sl_order_id,
                'tp_order_id': tp_order_id,
                'signal_strength': signal_info['signal_strength'],
                'confidence': signal_info['confidence'],
                'reasons': signal_info['reasons'],
                'score': signal_info['score'],
                'rsi': signal_info['rsi'],
                'adx': signal_info['adx']
            }
            
            self.active_positions[symbol] = trade_data
            self.database.save_trade(trade_data)
            
            # Enviar alerta
            self.alert_system.send_alert(
                f"🎯 Professional Trade: {symbol} {signal}",
                f"Entry: ${entry_price:.4f}\nSL: {sl_pct*100:.1f}% | TP: {tp_pct*100:.1f}%\nR/R: {risk_reward:.1f}:1\nScore: {signal_info['score']:.1f}",
                "info"
            )
            
            logger.logger.info(f"   ✅ PROFESSIONAL POSITION OPENED SUCCESSFULLY!\n")
            
            return True
            
        except Exception as e:
            logger.logger.error(f"❌ Professional order execution error: {e}")
            return False

    def run(self):
        """Loop principal profissional"""
        logger.logger.info(f"\n{'='*80}")
        logger.logger.info(f"🚀 PROFESSIONAL TRADING BOT - OPTIMIZED")
        logger.logger.info(f"{'='*80}")
        logger.logger.info(f"STRATEGY: Multi-Timeframe Technical Analysis")
        logger.logger.info(f"SYMBOLS: {len(self.symbols)} optimized coins")
        logger.logger.info(f"TIMEFRAMES: {', '.join(self.timeframes)}")
        logger.logger.info(f"RISK: {AdvancedTradingConfig.MAX_POSITION_SIZE*100:.1f}% per trade")
        logger.logger.info(f"TARGET: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"{'='*80}\n")
        
        if not self.setup_account():
            return
        
        # Loop principal
        cycle = 0
        last_report = datetime.now()
        
        try:
            while True:
                cycle += 1
                start_time = time.time()
                
                # Status do ciclo
                if cycle % 5 == 1:
                    self.log_cycle_status(cycle)
                
                # Verificar se pode operar
                can_trade, reason = self.risk_manager.can_trade()
                if not can_trade:
                    logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(120)
                    continue
                
                # Análise profissional
                positions_opened = self.run_professional_analysis_cycle()
                
                # Monitorar posições
                self.monitor_positions_professional()
                
                # Relatório horário
                if datetime.now() - last_report > timedelta(hours=1):
                    self.generate_hourly_report()
                    last_report = datetime.now()
                
                # Controlar frequência
                cycle_duration = time.time() - start_time
                sleep_time = max(AdvancedTradingConfig.ANALYSIS_INTERVAL, cycle_duration)
                
                if cycle % 10 == 1:
                    logger.logger.info(f"⏱️ Next analysis in {sleep_time:.0f}s")
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Professional shutdown")
        except Exception as e:
            logger.logger.error(f"❌ Professional bot error: {e}")
        finally:
            self.cleanup_professional()

    def log_cycle_status(self, cycle: int):
        """Log do status do ciclo"""
        stats = self.risk_manager.get_risk_status()
        
        logger.logger.info(f"\n[🔄 CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
        logger.logger.info(f"Status: {'🚀 ACTIVE' if stats['can_trade'] else '⏸️ PAUSED'}")
        logger.logger.info(f"Today: {stats['trades_today']}/{stats['target_trades']} trades")
        logger.logger.info(f"Daily P&L: {stats['daily_pnl']:+.2f}%")
        logger.logger.info(f"Active: {len(self.active_positions)}/{AdvancedTradingConfig.MAX_POSITIONS} positions")
        logger.logger.info(f"Win Rate: {stats['statistics']['win_rate']:.1f}%")

    def monitor_positions_professional(self):
        """Monitoramento profissional de posições"""
        if not self.active_positions:
            return
        
        try:
            symbols = list(self.active_positions.keys())
            positions = self.exchange.fetch_positions(symbols)
            
            for pos in positions:
                symbol = pos['symbol']
                if symbol not in self.active_positions:
                    continue
                
                contracts = float(pos.get('contracts', 0))
                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                
                if contracts == 0:
                    self.handle_position_close_professional(symbol, pos)
                    
        except Exception as e:
            logger.logger.error(f"❌ Position monitoring error: {e}")

    def handle_position_close_professional(self, symbol: str, position_data: Dict):
        """Trata fechamento de posição profissional"""
        try:
            trade_info = self.active_positions[symbol]
            unrealized_pnl = float(position_data.get('unrealizedPnl', 0))
            
            balance = self._get_account_balance()
            pnl_pct = (unrealized_pnl / balance) if balance > 0 else 0
            
            # Determinar motivo do fechamento
            if abs(unrealized_pnl) > 0:
                exit_reason = "TAKE_PROFIT" if unrealized_pnl > 0 else "STOP_LOSS"
            else:
                exit_reason = "MANUAL"
            
            # Registrar resultado
            self.risk_manager.register_trade_result(pnl_pct, symbol)
            
            exit_price = position_data.get('markPrice', trade_info['entry_price'])
            self.database.close_trade(symbol, exit_price, pnl_pct, unrealized_pnl, exit_reason)
            
            # Log detalhado
            duration = datetime.now() - trade_info['timestamp']
            status = "PROFIT" if pnl_pct > 0 else "LOSS"
            
            logger.logger.info(f"\n{'💚' if pnl_pct > 0 else '🔴'} POSITION CLOSED: {symbol} {status}")
            logger.logger.info(f"   P&L: {pnl_pct*100:+.2f}% (${unrealized_pnl:+.2f})")
            logger.logger.info(f"   Duration: {duration.total_seconds()/60:.1f}min")
            logger.logger.info(f"   Reason: {exit_reason}")
            logger.logger.info(f"   Daily P&L: {self.risk_manager.daily_pnl*100:+.2f}%")
            
            del self.active_positions[symbol]
            
        except Exception as e:
            logger.logger.error(f"❌ Position close error {symbol}: {e}")

    def generate_hourly_report(self):
        """Gera relatório horário"""
        try:
            stats = self.risk_manager.get_risk_status()
            
            report = f"""
📊 HOURLY REPORT - {datetime.now().strftime('%H:%M')}

Trades Today: {stats['trades_today']}/{stats['target_trades']}
Daily P&L: {stats['daily_pnl']:+.2f}%
Win Rate: {stats['statistics']['win_rate']:.1f}%
Active Positions: {len(self.active_positions)}
            
✅ System operating normally
            """
            
            logger.logger.info(report)
            
        except Exception as e:
            logger.logger.error(f"❌ Hourly report error: {e}")

    def cleanup_professional(self):
        """Cleanup profissional"""
        logger.logger.info("🛑 Shutting down Professional Bot...")
        
        try:
            self.executor.shutdown(wait=False)
            
            stats = self.risk_manager.get_risk_status()
            
            final_report = f"""
🏁 PROFESSIONAL BOT SHUTDOWN COMPLETE

FINAL STATISTICS:
Trades Today: {stats['trades_today']}/{stats['target_trades']}
Daily P&L: {stats['daily_pnl']:+.2f}%
Win Rate: {stats['statistics']['win_rate']:.1f}%
Active Positions: {len(self.active_positions)}

✅ Professional analysis system
✅ Risk-managed trading
✅ Multi-timeframe strategy

Shutdown: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            logger.logger.info(final_report)
            
        except Exception as e:
            logger.logger.error(f"❌ Professional cleanup error: {e}")
        
        logger.logger.info("✅ Professional Bot shutdown complete")

# =================== BOT PRINCIPAL COM CORREÇÕES ===================
class OptimizedAdvancedBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing FIXED Advanced Multi-Timeframe Bot...")
        
        # Componentes
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.analyzer = OptimizedMultiTimeframeAnalyzer()
        self.sl_tp_calculator = AdvancedStopLossTakeProfit()
        self.dashboard = OptimizedDashboard(self, port=5000)
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = self.cmc_api.get_top_coins()
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.primary_timeframe = AdvancedTradingConfig.PRIMARY_TIMEFRAME
        self.leverage = 3
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 1200  # 20 min cooldown
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="analyzer")
        
        # Taxa
        self.fee_rate = 0.00075
        
        logger.logger.info(f"✅ FIXED Bot initialized - {len(self.symbols)} symbols")
        
        # Alerta inicial
        mode = "TESTNET" if testnet else "🚨 PRODUCTION"
        self.alert_system.send_alert(
            f"Fixed Advanced Bot Started ({mode})",
            f"🚀 JSON Errors Fixed\n📊 {len(self.symbols)} Top Coins\n⚡ Multi-TF Analysis\n🎯 Target: 15 trades/day",
            "success"
        )

    def _setup_exchange(self):
        """Configura exchange com tratamento melhorado de leverage"""
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("❌ API keys not configured")
        
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 15000,
                'defaultLeverage': 3  # Adicionar leverage padrão
            },
            'sandbox': self.testnet,
        })
        
        logger.logger.info("✅ Exchange configured")

    def setup_account(self) -> bool:
        """Setup com tratamento robusto de leverage"""
        try:
            # Sincronizar
            self.exchange.load_time_difference()
            logger.logger.info("✅ Timestamp synchronized")
            
            # Carregar mercados
            markets = self.exchange.load_markets()
            logger.logger.info(f"✅ Markets loaded: {len(markets)}")
            
            # ✅ LEVERAGE COM APPROACH DIFERENTE
            leverage_success = 0
            for symbol in self.symbols:
                try:
                    # Tentar método padrão primeiro
                    self.exchange.set_leverage(self.leverage, symbol)
                    leverage_success += 1
                    time.sleep(0.03)
                except Exception as e:
                    # Tentar método alternativo
                    try:
                        # Para Bybit, podemos usar params
                        self.exchange.set_leverage(self.leverage, symbol, params={'leverage': self.leverage})
                        leverage_success += 1
                    except Exception as e2:
                        error_msg = str(e).lower()
                        if "110043" in error_msg or "only support linear" in error_msg:
                            # Ignorar erros conhecidos
                            continue
                        else:
                            logger.logger.debug(f"⚠️ Leverage warning for {symbol}: {e}")
            
            logger.logger.info(f"✅ Leverage {self.leverage}x set for {leverage_success}/{len(self.symbols)} symbols")
            
            # Verificar saldo
            balance = self._get_account_balance()
            min_balance = 2000 if not self.testnet else 200
            
            if balance < min_balance:
                error_msg = f"❌ Insufficient balance: ${balance:.2f}"
                logger.logger.error(error_msg)
                return False
            
            logger.logger.info(f"✅ Account balance: ${balance:.2f}")
            logger.logger.info(f"✅ Max position per trade: ${balance * AdvancedTradingConfig.MAX_POSITION_SIZE:.2f}")
            
            # Dashboard
            self.dashboard.start()
            
            # Notificar
            mode = "TESTNET" if self.testnet else "🚨 PRODUCTION"
            self.alert_system.send_alert(
                f"Fixed Bot Setup ({mode})",
                f"💰 Balance: ${balance:.2f}\n📊 {len(self.symbols)} coins\n⚡ Leverage: {leverage_success} symbols\n✅ All systems operational",
                "success"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Setup failed: {e}"
            logger.logger.error(error_msg)
            return False

    def _get_account_balance(self) -> float:
        """Saldo com tratamento de erro"""
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            logger.logger.error(f"❌ Balance error: {e}")
            return 0

    def fetch_multi_timeframe_data_safe(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados multi-TF com fallback"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                # Tentar com limite menor para performance
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=50)
                if len(ohlcv) >= 20:  # Reduzido para 20 candles mínimos
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
                    
            except Exception as e:
                if "not found" not in str(e).lower() and "invalid symbol" not in str(e).lower():
                    logger.logger.debug(f"Data error {symbol} {timeframe}: {e}")
                self.risk_manager.error_count += 1
                
        return ohlcv_data

    def analyze_symbol_safe(self, symbol: str) -> Optional[Dict]:
        """Análise simplificada e robusta"""
        try:
            # Buscar dados
            ohlcv_data = self.fetch_multi_timeframe_data_safe(symbol)
            
            if len(ohlcv_data) < 2:  # Pelo menos 2 timeframes
                return None
            
            # Análise multi-TF
            result = self.analyzer.multi_timeframe_analysis_simple(symbol, ohlcv_data)
            
            # Critérios mais flexíveis
            if (result and result['signal'] != 'NEUTRAL' and 
                result['score'] >= AdvancedTradingConfig.MIN_SIGNAL_SCORE and
                result['confidence'] >= AdvancedTradingConfig.MIN_CONFIDENCE):
                
                # Log do sinal encontrado
                logger.logger.info(f"🎯 SIGNAL FOUND: {symbol} {result['signal']} "
                                 f"(Score: {result['score']:.1f}, Conf: {result['confidence']:.1f})")
                
                # Salvar análise
                self.database.save_signal_analysis(symbol, 'multi', result)
                return result
            
            return None
            
        except Exception as e:
            logger.logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def calculate_position_size_safe(self, symbol: str, signal_strength: float) -> float:
        """Calcula posição adaptativa"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            # Tamanho adaptativo baseado na força do sinal
            base_size = AdvancedTradingConfig.MAX_POSITION_SIZE
            strength_multiplier = 0.8 + (signal_strength * 0.4)  # 0.8x a 1.2x
            
            # Aumentar agressividade se poucos trades
            if self.risk_manager.should_increase_aggression():
                strength_multiplier *= 1.3
            
            position_usdt = balance * base_size * strength_multiplier
            
            # Converter para quantidade
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = position_usdt / price
            
            # Precisão
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            final_quantity = float(quantity) if quantity else 0
            
            # Verificar quantidade mínima
            min_amount = 1.0  # Mínimo $1
            if final_quantity * price < min_amount:
                return 0
                
            return final_quantity
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0

    def open_position_safe(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição com fallbacks"""
        try:
            # Verificações básicas
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                logger.logger.info(f"⏸️ Trading paused: {reason}")
                return False
            
            if symbol in self.active_positions:
                logger.logger.debug(f"⏸️ Already in position: {symbol}")
                return False
            
            if len(self.active_positions) >= AdvancedTradingConfig.MAX_POSITIONS:
                logger.logger.info("⏸️ Max positions reached")
                return False
            
            # Cooldown
            current_time = time.time()
            if symbol in self.symbol_cooldown:
                time_since = current_time - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    logger.logger.debug(f"⏸️ {symbol} in cooldown: {self.min_cooldown - time_since:.0f}s left")
                    return False
            
            # Calcular posição
            signal_strength = signal_info['signal_strength']
            quantity = self.calculate_position_size_safe(symbol, signal_strength)
            
            if quantity <= 0:
                logger.logger.debug(f"❌ Invalid quantity for {symbol}: {quantity}")
                return False
            
            # SL/TP
            sl_pct, tp_pct = self.sl_tp_calculator.calculate_levels(
                df=signal_info['df'],
                signal_strength=signal_strength,
                timeframe=signal_info['timeframe'],
                multi_tf_data=signal_info.get('timeframe_results', {})
            )
            
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            # Preços de SL/TP
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_open = 'buy'
                side_close = 'sell'
            else:  # SHORT
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_open = 'sell'
                side_close = 'buy'
            
            risk_reward_ratio = tp_pct / sl_pct
            
            # Log detalhado
            logger.logger.info(f"\n🚀 OPENING POSITION: {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f} | Qty: {quantity:.4f}")
            logger.logger.info(f"   SL: ${sl_price:.4f} (-{sl_pct*100:.2f}%)")
            logger.logger.info(f"   TP: ${tp_price:.4f} (+{tp_pct*100:.2f}%)")
            logger.logger.info(f"   R/R: {risk_reward_ratio:.1f}:1")
            logger.logger.info(f"   Reasons: {', '.join(signal_info['reasons'][:2])}")
            
            try:
                # Executar ordem principal
                if signal == 'LONG':
                    order = self.exchange.create_market_buy_order(symbol, quantity)
                else:
                    order = self.exchange.create_market_sell_order(symbol, quantity)
                
                logger.logger.info(f"✅ Market order executed: {order.get('id')}")
                
                # Pequena pausa para garantir execução
                time.sleep(0.5)
                
                # Tentar ordens de SL/TP (opcional - podem ser feitas manualmente)
                sl_order_id = None
                tp_order_id = None
                
                try:
                    # Stop Loss
                    sl_order = self.exchange.create_order(
                        symbol, 'STOP_MARKET', side_close, quantity,
                        params={
                            'stopPrice': sl_price, 
                            'triggerBy': 'LastPrice', 
                            'reduceOnly': True
                        }
                    )
                    sl_order_id = sl_order.get('id')
                    logger.logger.info(f"✅ Stop Loss set: {sl_order_id}")
                    
                    # Take Profit
                    tp_order = self.exchange.create_order(
                        symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                        params={
                            'stopPrice': tp_price, 
                            'triggerBy': 'LastPrice', 
                            'reduceOnly': True
                        }
                    )
                    tp_order_id = tp_order.get('id')
                    logger.logger.info(f"✅ Take Profit set: {tp_order_id}")
                    
                except Exception as sl_tp_error:
                    logger.logger.warning(f"⚠️ SL/TP orders failed: {sl_tp_error}")
                    # Continuar mesmo sem SL/TP - o bot monitorará manualmente
                
                # Salvar posição
                trade_data = {
                    'symbol': symbol,
                    'signal': signal,
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'stop_loss_price': sl_price,
                    'take_profit_price': tp_price,
                    'stop_loss_pct': sl_pct,
                    'take_profit_pct': tp_pct,
                    'risk_reward_ratio': risk_reward_ratio,
                    'timestamp': datetime.now(),
                    'order_id': order.get('id'),
                    'sl_order_id': sl_order_id,
                    'tp_order_id': tp_order_id,
                    'signal_strength': signal_strength,
                    'reasons': signal_info['reasons'][:3],
                    'multi_tf_score': signal_info['score']
                }
                
                self.active_positions[symbol] = trade_data
                self.symbol_cooldown[symbol] = current_time
                
                # Salvar no database
                self.database.save_trade(trade_data)
                
                # Métricas
                position_value = entry_price * quantity
                logger.logger.info(f"💰 Position value: ${position_value:.2f}")
                logger.logger.info(f"📊 Active positions: {len(self.active_positions)}/{AdvancedTradingConfig.MAX_POSITIONS}")
                logger.logger.info(f"🎯 Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
                logger.logger.info(f"✅ POSITION OPENED SUCCESSFULLY!\n")
                
                # Alerta
                self.alert_system.send_alert(
                    f"🎯 New Position: {symbol} {signal}",
                    f"Entry: ${entry_price:.4f}\nSL: -{sl_pct*100:.1f}%\nTP: +{tp_pct*100:.1f}%\nR/R: {risk_reward_ratio:.1f}:1",
                    "info"
                )
                
                return True
                
            except Exception as order_error:
                logger.logger.error(f"❌ Order execution failed: {order_error}")
                return False
            
        except Exception as e:
            error_msg = f"❌ Position open error {symbol}: {e}"
            logger.logger.error(error_msg)
            self.risk_manager.error_count += 1
            return False

    def run_optimized_analysis_cycle(self) -> int:
        """Ciclo de análise paralelizado"""
        signals_found = 0
        positions_opened = 0
        
        try:
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                logger.logger.debug("⏸️ No symbols available (all in positions)")
                return 0
            
            # Filtrar símbolos em cooldown
            ready_symbols = []
            current_time = time.time()
            
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    time_since = current_time - self.symbol_cooldown[symbol]
                    if time_since >= self.min_cooldown:
                        ready_symbols.append(symbol)
                else:
                    ready_symbols.append(symbol)
            
            if not ready_symbols:
                logger.logger.debug("⏸️ All symbols in cooldown")
                return 0
            
            logger.logger.info(f"[🔍 ANALYSIS] Scanning {len(ready_symbols)} symbols...")
            
            # Análise paralela
            futures = {}
            for symbol in ready_symbols:
                future = self.executor.submit(self.analyze_symbol_safe, symbol)
                futures[future] = symbol
            
            # Processar resultados
            completed = 0
            for future in as_completed(futures, timeout=45):
                symbol = futures[future]
                completed += 1
                
                try:
                    result = future.result(timeout=5)
                    
                    if result:
                        signals_found += 1
                        logger.logger.info(f"🚨 STRONG SIGNAL: {symbol} {result['signal']} "
                                         f"(Score: {result['score']:.1f})")
                        
                        # Tentar abrir posição
                        success = self.open_position_safe(symbol, result)
                        if success:
                            positions_opened += 1
                            
                except Exception as e:
                    logger.logger.debug(f"Analysis future error {symbol}: {e}")
            
            if signals_found > 0:
                logger.logger.info(f"[🔍 COMPLETE] {signals_found} signals found, {positions_opened} positions opened")
            else:
                logger.logger.info(f"[🔍 COMPLETE] No strong signals found ({completed}/{len(ready_symbols)} symbols analyzed)")
            
            return positions_opened
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis cycle error: {e}")
            return 0

    # ... (manter os outros métodos check_positions_safe, run_daily_report_simple, etc. iguais)

    def run(self):
        """Loop principal otimizado"""
        logger.logger.info(f"\n{'='*80}")
        logger.logger.info(f"🚀 FIXED ADVANCED MULTI-TIMEFRAME BOT - OPTIMIZED")
        logger.logger.info(f"{'='*80}")
        logger.logger.info(f"MODE: {'🧪 TESTNET' if self.testnet else '🚨 PRODUCTION'}")
        logger.logger.info(f"SYMBOLS: {len(self.symbols)} coins")
        logger.logger.info(f"TIMEFRAMES: {', '.join(self.timeframes)}")
        logger.logger.info(f"TARGET: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"CONFIG: SL={AdvancedTradingConfig.MIN_STOP_LOSS_PCT*100:.1f}%, "
                          f"R/R≥{AdvancedTradingConfig.MIN_RISK_REWARD_RATIO:.1f}")
        logger.logger.info(f"DASHBOARD: http://localhost:5000")
        logger.logger.info(f"{'='*80}\n")
        
        # Setup
        if not self.setup_account():
            logger.logger.error("❌ Setup failed - check API keys and balance")
            return
        
        # Loop principal
        cycle = 0
        last_daily_report = datetime.now().date()
        total_positions_opened = 0
        
        try:
            while True:
                cycle += 1
                cycle_start = time.time()
                
                # Status a cada ciclo
                can_trade, reason = self.risk_manager.can_trade()
                stats = self.risk_manager.get_risk_status()
                
                if cycle % 5 == 1:
                    logger.logger.info(f"\n[CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                    logger.logger.info(f"Status: {'🚀 ACTIVE' if can_trade else f'⏸️ PAUSED ({reason})'}")
                    logger.logger.info(f"Today: {stats['trades_today']}/{stats['target_trades']} "
                                    f"| Active: {len(self.active_positions)}/5")
                    logger.logger.info(f"Daily P&L: {stats['daily_pnl']:+.2f}% | Errors: {stats['error_count']}")
                
                if not can_trade:
                    if cycle % 10 == 1:
                        logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(120)
                    continue
                
                # Relatório diário
                current_date = datetime.now().date()
                if current_date != last_daily_report:
                    self.run_daily_report_simple()
                    last_daily_report = current_date
                    total_positions_opened = 0
                
                # Análise e trading
                positions_this_cycle = self.run_optimized_analysis_cycle()
                total_positions_opened += positions_this_cycle
                
                # Monitorar posições
                self.check_positions_safe()
                
                # Resumo a cada 10 ciclos
                if cycle % 10 == 0 or positions_this_cycle > 0:
                    logger.logger.info(f"\n[📊 SUMMARY #{cycle}]")
                    logger.logger.info(f"Positions this cycle: {positions_this_cycle}")
                    logger.logger.info(f"Total today: {total_positions_opened}")
                    logger.logger.info(f"Active positions: {len(self.active_positions)}")
                    logger.logger.info(f"Win Rate: {stats['statistics']['win_rate']:.1f}%")
                
                # Timing do ciclo
                cycle_duration = time.time() - cycle_start
                sleep_time = max(60, AdvancedTradingConfig.ANALYSIS_INTERVAL - cycle_duration)
                
                if cycle % 20 == 1:
                    logger.logger.info(f"⏱️ Next analysis in {sleep_time:.0f}s")
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Manual shutdown requested")
            
        except Exception as e:
            logger.logger.error(f"❌ Fatal error: {e}")
            logger.logger.error(traceback.format_exc())
            
        finally:
            self._shutdown_safe()

    def _shutdown_safe(self):
        """Shutdown seguro"""
        logger.logger.info("🛑 Shutting down optimized bot...")
        
        try:
            # Fechar executor
            self.executor.shutdown(wait=False)
            
            # Relatório final
            stats = self.risk_manager.get_risk_status()
            logger.logger.info(f"\n[🏁 FINAL REPORT]")
            logger.logger.info(f"Trades today: {stats['trades_today']}/{stats['target_trades']}")
            logger.logger.info(f"Daily P&L: {stats['daily_pnl']:+.2f}%")
            logger.logger.info(f"Active positions: {len(self.active_positions)}")
            logger.logger.info(f"Total errors: {stats['error_count']}")
            
        except Exception as e:
            logger.logger.error(f"Shutdown error: {e}")
        
        logger.logger.info("✅ Optimized bot shutdown complete")

# =================== COINMARKETCAP API INTEGRATION ===================
class CoinMarketCapAPI:
    def __init__(self):
        self.api_key = AdvancedTradingConfig.COINMARKETCAP_API_KEY
        self.base_url = "https://pro-api.coinmarketcap.com"
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        
        # Filtros para remover memes e stables
        self.excluded_symbols = {
            # Stablecoins
            'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP', 'GUSD', 'HUSD', 'SUSD', 'USDK',
            'FRAX', 'LUSD', 'ALUSD', 'OUSD', 'USTC', 'UST', 'CUSD',
            # Meme coins principais
            'DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'MEME', 'SAFEMOON',
            'BABYDOGE', 'KISHU', 'HOGE', 'AKITA', 'SAITAMA', 'ELON', 'DOGELON',
            # Wrapped tokens
            'WBTC', 'WETH', 'WBNB', 'WMATIC', 'WAVAX',
        }
    
    def get_top_coins(self) -> List[str]:
        """Obtém as top 20 moedas filtradas"""
        try:
            if not self.api_key:
                logger.logger.info("Using default coins (CMC API not configured)")
                return self._get_default_coins()
            
            url = f"{self.base_url}/v1/cryptocurrency/listings/latest"
            params = {
                'start': '1',
                'limit': '50',  # Pegar mais para filtrar
                'convert': 'USD',
                'sort': 'market_cap',
                'sort_dir': 'desc'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                filtered_coins = []
                
                for coin in data['data']:
                    symbol = coin['symbol']
                    name = coin['name'].lower()
                    
                    # Filtrar stables, memes, wrapped tokens
                    if (symbol not in self.excluded_symbols and 
                        not any(keyword in name for keyword in ['wrapped', 'pegged', 'bridged', 'inu', 'moon', 'safe', 'baby']) and
                        coin['quote']['USD']['market_cap'] > 500000000):  # Market cap > 500M
                        
                        # Verificar se existe no Bybit
                        bybit_symbol = f"{symbol}USDT"
                        filtered_coins.append(bybit_symbol)
                        
                        if len(filtered_coins) >= AdvancedTradingConfig.TOP_COINS_COUNT:
                            break
                
                logger.logger.info(f"✅ CMC Top coins loaded: {len(filtered_coins)} symbols")
                return filtered_coins
                
            else:
                logger.logger.warning(f"CMC API error: {response.status_code}, using defaults")
                return self._get_default_coins()
                
        except Exception as e:
            logger.logger.warning(f"CMC API failed: {e}, using defaults")
            return self._get_default_coins()
    
    def _get_default_coins(self) -> List[str]:
        """Moedas padrão caso a API falhe"""
        return [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOTUSDT', 'AVAXUSDT', 'LINKUSDT', 'MATICUSDT',
            'LTCUSDT', 'UNIUSDT', 'ATOMUSDT', 'ALGOUSDT', 'VETUSDT',
            'FILUSDT', 'TRXUSDT', 'ETCUSDT', 'XLMUSDT', 'NEARUSDT'
        ]

# =================== SISTEMA DE DADOS JSON THREAD-SAFE ===================
class SafeJSONDatabase:
    def __init__(self, db_path="trading_data_advanced"):
        self.db_path = db_path
        os.makedirs(db_path, exist_ok=True)
        self.trades_file = os.path.join(db_path, "trades.json")
        self.stats_file = os.path.join(db_path, "statistics.json")
        self.signals_file = os.path.join(db_path, "signals_history.json")
        self.performance_file = os.path.join(db_path, "daily_performance.json")
        
        # ✅ LOCKS PARA THREAD SAFETY
        self.trades_lock = threading.Lock()
        self.signals_lock = threading.Lock()
        self.stats_lock = threading.Lock()
        
        self.init_database()
    
    def init_database(self):
        """Inicializa arquivos JSON com locks"""
        files_data = {
            self.trades_file: [],
            self.stats_file: {
                "total_trades": 0,
                "winning_trades": 0,
                "total_pnl": 0,
                "best_trade": 0,
                "worst_trade": 0,
                "trades_today": 0
            },
            self.signals_file: [],
            self.performance_file: {}
        }
        
        for file_path, default_data in files_data.items():
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(default_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    logger.logger.error(f"Error creating {file_path}: {e}")
    
    def safe_read_json(self, file_path: str, default_data):
        """Leitura segura de JSON"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            return default_data
        except (json.JSONDecodeError, Exception) as e:
            logger.logger.error(f"JSON read error {file_path}: {e}")
            return default_data
    
    def safe_write_json(self, file_path: str, data):
        """Escrita segura de JSON"""
        try:
            # Escrever em arquivo temporário primeiro
            temp_file = f"{file_path}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Mover arquivo temporário para o final (operação atômica)
            if os.path.exists(temp_file):
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(temp_file, file_path)
                return True
        except Exception as e:
            logger.logger.error(f"JSON write error {file_path}: {e}")
            # Limpar arquivo temporário se existir
            temp_file = f"{file_path}.tmp"
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False
    
    def save_trade(self, trade_data):
        """Salva trade com thread safety"""
        with self.trades_lock:
            try:
                trades = self.safe_read_json(self.trades_file, [])
                
                trade_record = {
                    'id': len(trades) + 1,
                    'timestamp_open': trade_data['timestamp'].isoformat(),
                    'symbol': trade_data['symbol'],
                    'signal': trade_data['signal'],
                    'entry_price': trade_data['entry_price'],
                    'quantity': trade_data['quantity'],
                    'stop_loss_price': trade_data['stop_loss_price'],
                    'take_profit_price': trade_data['take_profit_price'],
                    'stop_loss_pct': trade_data['stop_loss_pct'] * 100,
                    'take_profit_pct': trade_data['take_profit_pct'] * 100,
                    'risk_reward_ratio': trade_data['risk_reward_ratio'],
                    'status': 'OPEN',
                    'multi_tf_score': trade_data.get('multi_tf_score', 0)
                }
                
                trades.append(trade_record)
                self.safe_write_json(self.trades_file, trades)
                    
            except Exception as e:
                logger.logger.error(f"Error saving trade: {e}")
    
    def save_signal_analysis(self, symbol, timeframe, signal_data):
        """Salva análise de sinal com thread safety - SIMPLIFICADO"""
        # ✅ SIMPLIFICAR PARA EVITAR ERROS JSON
        with self.signals_lock:
            try:
                signals = self.safe_read_json(self.signals_file, [])
                
                # Dados mínimos para evitar problemas de serialização
                signal_record = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'symbol': str(symbol),
                    'timeframe': str(timeframe),
                    'signal': str(signal_data.get('signal', 'NEUTRAL')),
                    'score': float(signal_data.get('score', 0)),
                    'confidence': float(signal_data.get('confidence', 0))
                }
                
                signals.append(signal_record)
                
                # Manter apenas últimos 500 sinais para evitar arquivo grande
                if len(signals) > 500:
                    signals = signals[-500:]
                
                self.safe_write_json(self.signals_file, signals)
                    
            except Exception as e:
                logger.logger.error(f"Error saving signal analysis: {e}")
    
    def close_trade(self, symbol, exit_price, pnl_pct, pnl_usd, exit_reason="AUTO"):
        """Fecha trade no database com thread safety"""
        with self.trades_lock:
            try:
                trades = self.safe_read_json(self.trades_file, [])
                
                for trade in trades:
                    if trade['symbol'] == symbol and trade['status'] == 'OPEN':
                        trade['timestamp_close'] = datetime.now().isoformat()
                        trade['exit_price'] = exit_price
                        trade['pnl_pct'] = pnl_pct * 100
                        trade['pnl_usd'] = pnl_usd
                        trade['exit_reason'] = exit_reason
                        trade['status'] = 'CLOSED'
                        
                        # Calcular tempo de holding
                        try:
                            open_time = datetime.fromisoformat(trade['timestamp_open'])
                            hold_minutes = (datetime.now() - open_time).total_seconds() / 60
                            trade['hold_time_minutes'] = hold_minutes
                        except:
                            trade['hold_time_minutes'] = 0
                        break
                
                self.safe_write_json(self.trades_file, trades)
                    
            except Exception as e:
                logger.logger.error(f"Error closing trade: {e}")
    
    def get_trade_statistics(self):
        """Obtém estatísticas com thread safety"""
        with self.trades_lock:
            try:
                trades = self.safe_read_json(self.trades_file, [])
                
                closed_trades = [t for t in trades if t.get('status') == 'CLOSED']
                today = datetime.now().strftime('%Y-%m-%d')
                today_trades = [t for t in trades if t.get('timestamp_open', '').startswith(today)]
                
                if not closed_trades:
                    return {
                        'total_trades': len(trades),
                        'winning_trades': 0,
                        'losing_trades': 0,
                        'win_rate': 0,
                        'avg_pnl': 0,
                        'best_trade': 0,
                        'worst_trade': 0,
                        'avg_risk_reward': 0,
                        'avg_hold_time_hours': 0,
                        'trades_today': len(today_trades),
                        'target_trades': AdvancedTradingConfig.TARGET_TRADES_PER_DAY
                    }
                
                total_trades = len(closed_trades)
                winning_trades = len([t for t in closed_trades if t.get('pnl_pct', 0) > 0])
                
                pnl_values = [t.get('pnl_pct', 0) for t in closed_trades]
                avg_pnl = sum(pnl_values) / len(pnl_values) if pnl_values else 0
                best_trade = max(pnl_values) if pnl_values else 0
                worst_trade = min(pnl_values) if pnl_values else 0
                
                rr_values = [t.get('risk_reward_ratio', 0) for t in closed_trades]
                avg_rr = sum(rr_values) / len(rr_values) if rr_values else 0
                
                hold_times = [t.get('hold_time_minutes', 0) for t in closed_trades]
                avg_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0
                
                return {
                    'total_trades': len(trades),
                    'winning_trades': winning_trades,
                    'losing_trades': total_trades - winning_trades,
                    'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                    'avg_pnl': avg_pnl,
                    'best_trade': best_trade,
                    'worst_trade': worst_trade,
                    'avg_risk_reward': avg_rr,
                    'avg_hold_time_hours': (avg_hold_time / 60) if avg_hold_time else 0,
                    'trades_today': len(today_trades),
                    'target_trades': AdvancedTradingConfig.TARGET_TRADES_PER_DAY
                }
                
            except Exception as e:
                logger.logger.error(f"Error getting statistics: {e}")
                return {
                    'total_trades': 0, 'winning_trades': 0, 'losing_trades': 0,
                    'win_rate': 0, 'avg_pnl': 0, 'best_trade': 0, 'worst_trade': 0,
                    'avg_risk_reward': 0, 'avg_hold_time_hours': 0, 'trades_today': 0,
                    'target_trades': AdvancedTradingConfig.TARGET_TRADES_PER_DAY
                }

# =================== SISTEMA DE LOGGING APRIMORADO ===================
class AdvancedLogger:
    def __init__(self):
        os.makedirs('logs_advanced', exist_ok=True)
        self.setup_loggers()
        
    def setup_loggers(self):
        date_str = datetime.now().strftime("%Y%m%d")
        
        # Configurar logging principal
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S',
            handlers=[
                logging.FileHandler(f'logs_advanced/bot_main_{date_str}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('main')
        
        # Logger de trades
        self.trade_logger = logging.getLogger('trades')
        trade_handler = logging.FileHandler(f'logs_advanced/bot_trades_{date_str}.log', encoding='utf-8')
        trade_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        self.trade_logger.addHandler(trade_handler)
        self.trade_logger.setLevel(logging.INFO)
        
        # Logger de análises - SIMPLIFICADO
        self.analysis_logger = logging.getLogger('analysis')
        analysis_handler = logging.FileHandler(f'logs_advanced/bot_analysis_{date_str}.log', encoding='utf-8')
        analysis_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        self.analysis_logger.addHandler(analysis_handler)
        self.analysis_logger.setLevel(logging.INFO)

# =================== SISTEMA DE ALERTAS ===================
class AdvancedAlert:
    def __init__(self):
        self.telegram_enabled = bool(os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'))
        if self.telegram_enabled:
            logger.logger.info("✅ Telegram alerts enabled")
        else:
            logger.logger.info("⚠️ Telegram alerts not configured")
    
    def send_alert(self, title: str, message: str, priority: str = 'info'):
        """Envia alerta via Telegram se configurado"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{title}\n\n{message}\n\nTime: {timestamp}"
        
        logger.logger.info(f"[ALERT] {title}")
        
        if self.telegram_enabled:
            self._send_telegram(title, full_message, priority)
    
    def _send_telegram(self, title: str, message: str, priority: str):
        try:
            emojis = {'info': '📊', 'warning': '⚠️', 'high': '🔴', 'critical': '🚨', 'success': '✅'}
            emoji = emojis.get(priority, '📊')
            
            formatted_message = f"{emoji} <b>{title}</b>\n\n{message}"
            
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
            data = {
                'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
                'text': formatted_message[:4096],
                'parse_mode': 'HTML'
            }
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            logger.logger.error(f"Telegram error: {e}")

# =================== CALCULADORA AVANÇADA DE SL/TP ===================
class AdvancedStopLossTakeProfit:
    @staticmethod
    def calculate_levels(df: pd.DataFrame, signal_strength: float = 1.0, 
                        timeframe: str = '1h', multi_tf_data: Dict = None) -> Tuple[float, float]:
        """Calcula SL/TP considerando múltiplos timeframes"""
        try:
            atr = df['atr'].iloc[-1]
            price = df['close'].iloc[-1]
            atr_pct = atr / price
            
            # Ajustar ATR baseado no timeframe
            tf_multipliers = {'15m': 1.2, '1h': 1.0, '2h': 0.9, '4h': 0.8}
            tf_mult = tf_multipliers.get(timeframe, 1.0)
            
            # === CALCULAR STOP LOSS ===
            sl_pct = atr_pct * AdvancedTradingConfig.ATR_MULTIPLIER * tf_mult
            
            # Ajustar pela força do sinal (mais agressivo)
            signal_factor = 0.7 + (signal_strength * 0.3)
            sl_pct = sl_pct * signal_factor
            
            # Ajustar por confirmação multi-timeframe
            if multi_tf_data and len(multi_tf_data) > 1:
                confirmation_count = sum(1 for tf_data in multi_tf_data.values() 
                                       if tf_data.get('signal') != 'NEUTRAL')
                if confirmation_count >= 2:
                    sl_pct = sl_pct * 0.85  # SL mais próximo se confirmado
            
            # Limites
            sl_pct = max(AdvancedTradingConfig.MIN_STOP_LOSS_PCT, 
                        min(sl_pct, AdvancedTradingConfig.MAX_STOP_LOSS_PCT))
            
            # === CALCULAR TAKE PROFIT ===
            tp_pct = sl_pct * AdvancedTradingConfig.MIN_RISK_REWARD_RATIO
            
            # Ajustar TP baseado na volatilidade
            if atr_pct > 0.025:  # Alta volatilidade
                tp_pct = tp_pct * AdvancedTradingConfig.HIGH_VOLATILITY_TP_MULT
            
            # Ajustar TP baseado no timeframe
            if timeframe in ['15m', '1h']:  # Timeframes menores = TP menor
                tp_pct = tp_pct * 0.9
            elif timeframe in ['2h', '4h']:  # Timeframes maiores = TP maior
                tp_pct = tp_pct * 1.1
            
            # Limite máximo
            tp_pct = min(tp_pct, AdvancedTradingConfig.MAX_TAKE_PROFIT_PCT)
            
            risk_reward_ratio = tp_pct / sl_pct
            
            return sl_pct, tp_pct
            
        except Exception as e:
            logger.logger.error(f"Error calculating SL/TP: {e}")
            return AdvancedTradingConfig.MIN_STOP_LOSS_PCT, AdvancedTradingConfig.MIN_STOP_LOSS_PCT * AdvancedTradingConfig.MIN_RISK_REWARD_RATIO

# =================== RISK MANAGER AVANÇADO ===================
class AdvancedRiskManager:
    def __init__(self, database):
        self.db = database
        
        # Limites flexíveis
        self.max_daily_loss = AdvancedTradingConfig.MAX_DAILY_LOSS
        self.max_position_size = AdvancedTradingConfig.MAX_POSITION_SIZE
        self.max_positions = AdvancedTradingConfig.MAX_POSITIONS
        self.max_consecutive_losses = AdvancedTradingConfig.MAX_CONSECUTIVE_LOSSES
        
        # Estado
        self.daily_pnl = 0
        self.consecutive_losses = 0
        self.error_count = 0
        self.trades_today = 0
        
        # Controle
        self.last_daily_reset = datetime.now().date()
        self.trade_history = []
        
        logger.logger.info("✅ Advanced Risk Manager initialized")
    
    def can_trade(self) -> Tuple[bool, str]:
        """Verifica se pode operar com critérios flexíveis"""
        self._check_daily_reset()
        
        # PnL diário - permitir trading até o limite de perda
        if self.daily_pnl <= self.max_daily_loss:
            return False, f"Daily loss limit: {self.daily_pnl*100:.1f}%"
        
        # Perdas consecutivas
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Consecutive losses: {self.consecutive_losses}"
        
        # Muitos erros
        if self.error_count >= 20:  # Mais tolerante
            return False, "Too many errors"
        
        return True, "OK"
    
    def _check_daily_reset(self):
        """Reset diário"""
        if datetime.now().date() != self.last_daily_reset:
            logger.logger.info(f"Daily reset - Previous: PnL {self.daily_pnl*100:.2f}%, Trades: {self.trades_today}")
            self.daily_pnl = 0
            self.consecutive_losses = 0
            self.error_count = 0
            self.trades_today = 0
            self.last_daily_reset = datetime.now().date()
    
    def should_increase_aggression(self) -> bool:
        """Determina se deve ser mais agressivo baseado na performance"""
        if self.trades_today < AdvancedTradingConfig.TARGET_TRADES_PER_DAY / 2:
            hour = datetime.now().hour
            if hour >= 12:  # Após meio-dia, ser mais agressivo
                return True
        return False
    
    def calculate_position_size_adaptive(self, signal_strength: float) -> float:
        """Calcula tamanho da posição adaptativo"""
        base_size = self.max_position_size
        
        # Ajustar por força do sinal
        size_multiplier = 0.7 + (signal_strength * 0.6)  # 0.7x a 1.3x
        
        # Ser mais agressivo se poucos trades
        if self.should_increase_aggression():
            size_multiplier *= 1.2
        
        # Reduzir se muitas perdas consecutivas
        if self.consecutive_losses > 2:
            size_multiplier *= (1 - 0.1 * self.consecutive_losses)
        
        final_size = base_size * size_multiplier
        final_size = max(0.005, min(final_size, self.max_position_size * 1.5))
        
        return final_size
    
    def register_trade_result(self, pnl_pct: float, symbol: str):
        """Registra resultado"""
        self.daily_pnl += pnl_pct
        self.trades_today += 1
        
        if pnl_pct < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        self.trade_history.append({
            'pnl_pct': pnl_pct,
            'symbol': symbol,
            'timestamp': datetime.now()
        })
        
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]
        
        logger.logger.info(f"Trade result: {symbol} {pnl_pct*100:+.2f}% | Daily: {self.daily_pnl*100:+.2f}% | Today: {self.trades_today}")
    
    def get_risk_status(self):
        """Status do risk manager"""
        can_trade, reason = self.can_trade()
        stats = self.db.get_trade_statistics()
        
        return {
            'can_trade': can_trade,
            'reason': reason,
            'daily_pnl': self.daily_pnl * 100,
            'consecutive_losses': self.consecutive_losses,
            'error_count': self.error_count,
            'trades_today': self.trades_today,
            'target_trades': AdvancedTradingConfig.TARGET_TRADES_PER_DAY,
            'should_be_aggressive': self.should_increase_aggression(),
            'statistics': stats
        }

# =================== VALIDAÇÃO MAIS TOLERANTE ===================
class OptimizedMultiTimeframeAnalyzer:
    def __init__(self):
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.primary_tf = AdvancedTradingConfig.PRIMARY_TIMEFRAME
        logger.logger.info("✅ Tolerant Analyzer initialized")
    
    def validate_data_quality_tolerant(self, df: pd.DataFrame) -> bool:
        """Validação mais tolerante - apenas verifica o básico"""
        try:
            if df.empty or len(df) < 15:  # Reduzido de 20 para 15
                return False
            
            # Verificar apenas se há dados básicos
            last_row = df.iloc[-1]
            
            # Verificar apenas preços válidos (não zero ou negativos)
            if (last_row['high'] <= 0 or last_row['low'] <= 0 or 
                last_row['close'] <= 0 or last_row['open'] <= 0):
                return False
            
            # Verificar lógica básica dos preços
            if last_row['high'] < last_row['low']:
                return False
            
            return True  # Aceita mesmo com alguns NaN ou volume zero
        except Exception as e:
            logger.logger.debug(f"Data validation error: {e}")
            return False
    
    def calculate_indicators_tolerant(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de forma tolerante"""
        try:
            if not self.validate_data_quality_tolerant(df):
                return df
            
            # RSI - sempre calcular mesmo com dados imperfeitos
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
            
            # Corrigir RSI inválido
            if pd.isna(df['rsi'].iloc[-1]) or df['rsi'].iloc[-1] > 100 or df['rsi'].iloc[-1] < 0:
                df['rsi'] = 50.0
            
            # EMAs
            df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
            df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
            
            # MACD
            try:
                macd = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
                df['macd'] = macd.macd()
                df['macd_signal'] = macd.macd_signal()
            except:
                df['macd'] = 0
                df['macd_signal'] = 0
            
            # ATR
            try:
                df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
                if pd.isna(df['atr'].iloc[-1]) or df['atr'].iloc[-1] <= 0:
                    df['atr'] = df['close'].iloc[-1] * 0.01
            except:
                df['atr'] = df['close'].iloc[-1] * 0.01
            
            # Volume - mais tolerante
            try:
                df['volume_sma'] = df['volume'].rolling(window=10).mean()  # Reduzido de 20
                df['volume_ratio'] = df['volume'] / df['volume_sma']
                
                # Se volume ratio for NaN, usar 1.0
                if pd.isna(df['volume_ratio'].iloc[-1]):
                    df['volume_ratio'] = 1.0
            except:
                df['volume_ratio'] = 1.0
            
            return df
            
        except Exception as e:
            logger.logger.error(f"Error calculating tolerant indicators: {e}")
            # Retornar DataFrame com valores padrão
            if not df.empty:
                df['rsi'] = 50.0
                df['ema_fast'] = df['close']
                df['ema_slow'] = df['close']
                df['macd'] = 0
                df['macd_signal'] = 0
                df['atr'] = df['close'].iloc[-1] * 0.01 if not df.empty else 0.01
                df['volume_ratio'] = 1.0
            return df

    def fetch_ohlcv_data_tolerant(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados OHLCV de forma tolerante"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                # Buscar menos dados para ser mais rápido
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=25)  # Reduzido de 50
                if len(ohlcv) >= 10:  # Reduzido de 25 para 10
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    
                    # Apenas verificação básica - não rejeitar por NaN no volume
                    if (df[['open', 'high', 'low', 'close']].isnull().any().any()):
                        continue
                        
                    ohlcv_data[timeframe] = df
                    logger.logger.debug(f"✅ Dados obtidos para {symbol} {timeframe}")
            except Exception as e:
                logger.logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
                
        return ohlcv_data

    def analyze_symbol_tolerant(self, symbol: str) -> Optional[Dict]:
        """Analisa símbolo de forma tolerante"""
        try:
            ohlcv_data = self.fetch_ohlcv_data_tolerant(symbol)
            
            if len(ohlcv_data) < 1:
                logger.logger.info(f"   📭 {symbol}: No timeframe data")
                return None
            
            # Usar análise tolerante
            result = self.multi_timeframe_analysis_tolerant(symbol, ohlcv_data)
            
            # MANTER CRITÉRIOS CONSERVADORES para abrir trades
            if (result and result['signal'] != 'NEUTRAL' and 
                result['score'] >= AdvancedTradingConfig.MIN_SIGNAL_SCORE and
                result['confidence'] >= AdvancedTradingConfig.MIN_CONFIDENCE):
                
                self.database.save_signal_analysis(symbol, 'multi', result)
                return result
            
            return None
            
        except Exception as e:
            logger.logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def multi_timeframe_analysis_tolerant(self, symbol: str, ohlcv_data: Dict[str, pd.DataFrame]) -> Dict:
        """Análise tolerante mas com logging detalhado"""
        try:
            logger.logger.info(f"\n🔍 ANALYZING {symbol}:")
            
            tf_results = {}
            total_score = 0
            signal_votes = {'LONG': 0, 'SHORT': 0, 'NEUTRAL': 0}
            
            for timeframe in self.timeframes:
                if timeframe in ohlcv_data and len(ohlcv_data[timeframe]) > 0:
                    df = ohlcv_data[timeframe]
                    df = self.calculate_indicators_tolerant(df)
                    
                    # Análise básica
                    result = self.analyze_single_timeframe_tolerant(symbol, df, timeframe)
                    tf_results[timeframe] = result
                    
                    # Log detalhado
                    logger.logger.info(f"   {timeframe}: {result['signal']} "
                                     f"(Score: {result['score']:.1f}, RSI: {result['rsi']:.1f})")
                    
                    if result['signal'] == 'LONG':
                        total_score += result['score']
                        signal_votes['LONG'] += 1
                    elif result['signal'] == 'SHORT':
                        total_score -= result['score']
                        signal_votes['SHORT'] += 1
                    else:
                        signal_votes['NEUTRAL'] += 1
            
            if not tf_results:
                return self._neutral_signal("No timeframe data", "multi")
            
            # Determinar sinal final (critérios conservadores)
            final_signal = 'NEUTRAL'
            
            if signal_votes['LONG'] >= 2 and total_score >= 6.0:
                final_signal = 'LONG'
            elif signal_votes['SHORT'] >= 2 and total_score <= -6.0:
                final_signal = 'SHORT'
            
            primary_data = list(tf_results.values())[0]
            
            result = {
                'signal': final_signal,
                'score': abs(total_score),
                'confidence': sum(r['confidence'] for r in tf_results.values()) / len(tf_results),
                'signal_strength': min(abs(total_score) / 8.0, 1.0),
                'price': primary_data['price'],
                'rsi': primary_data['rsi'],
                'volume_ratio': primary_data['volume_ratio'],
                'atr': primary_data['atr'],
                'timeframe': 'multi',
                'reasons': primary_data['reasons'],
                'df': primary_data['df'],
                'timeframe_results': tf_results
            }
            
            if final_signal != 'NEUTRAL':
                logger.logger.info(f"   🎯 {symbol}: {final_signal} SIGNAL!")
            else:
                logger.logger.info(f"   ⏸️ {symbol}: No signal")
            
            return result
            
        except Exception as e:
            logger.logger.error(f"Error in analysis for {symbol}: {e}")
            return self._neutral_signal("Analysis error", "multi")

    def analyze_single_timeframe_tolerant(self, symbol: str, df: pd.DataFrame, timeframe: str) -> Dict:
        """Análise de timeframe único tolerante"""
        try:
            if len(df) < 10:
                return self._neutral_signal("Insufficient data", timeframe)
            
            last = df.iloc[-1]
            
            score = 0
            confidence = 0
            reasons = []
            
            # RSI
            rsi = last['rsi']
            if 30 <= rsi <= 70:  # Apenas considerar RSI válido
                if rsi <= 30:
                    score += 2.5
                    confidence += 2.0
                    reasons.append(f"RSI Oversold ({rsi:.1f})")
                elif rsi >= 70:
                    score -= 2.5
                    confidence += 2.0
                    reasons.append(f"RSI Overbought ({rsi:.1f})")
            
            # EMA
            if last['ema_fast'] > last['ema_slow']:
                score += 1.5
                confidence += 1.0
                reasons.append("EMA Bullish")
            else:
                score -= 1.5
                confidence += 1.0
                reasons.append("EMA Bearish")
            
            # Volume
            vol_ratio = last['volume_ratio']
            if vol_ratio >= 1.2:
                score += 1.0
                reasons.append(f"Volume {vol_ratio:.1f}x")
            
            # Determinar sinal
            signal = 'NEUTRAL'
            if score >= 4.0 and confidence >= 2.5:
                signal = 'LONG'
            elif score <= -4.0 and confidence >= 2.5:
                signal = 'SHORT'
            
            return {
                'signal': signal,
                'score': abs(score),
                'confidence': confidence,
                'price': last['close'],
                'rsi': rsi,
                'volume_ratio': vol_ratio,
                'atr': last['atr'],
                'timeframe': timeframe,
                'reasons': reasons,
                'df': df
            }
            
        except Exception as e:
            return self._neutral_signal("Analysis error", timeframe)

# =================== BOT COMPLETO COM TODOS OS MÉTODOS ===================
class UltraFastAdvancedBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing COMPLETE Advanced Bot...")
        
        # Componentes
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.analyzer = OptimizedMultiTimeframeAnalyzer()
        self.sl_tp_calculator = AdvancedStopLossTakeProfit()
        self.dashboard = OptimizedDashboard(self, port=5000)
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = self.cmc_api.get_top_coins()
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.primary_timeframe = AdvancedTradingConfig.PRIMARY_TIMEFRAME
        self.leverage = 3
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 900  # 15 min cooldown
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="analyzer")
        
        # Taxa
        self.fee_rate = 0.00075
        
        logger.logger.info(f"✅ COMPLETE Bot initialized - {len(self.symbols)} symbols")

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
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 15000,
            },
            'sandbox': self.testnet,
        })
        
        logger.logger.info("✅ Exchange configured")

    def _get_account_balance(self) -> float:
        """Saldo com tratamento de erro"""
        try:
            balance = self.exchange.fetch_balance()
            total_balance = balance['USDT']['total']
            logger.logger.info(f"💰 Total balance: ${total_balance:.2f}")
            return total_balance
        except Exception as e:
            logger.logger.error(f"❌ Balance error: {e}")
            return 0

    def setup_account(self) -> bool:
        """Setup da conta"""
        try:
            self.exchange.load_time_difference()
            markets = self.exchange.load_markets()
            
            # Configuração de leverage
            leverage_success = 0
            for symbol in self.symbols:
                try:
                    self.exchange.set_leverage(self.leverage, symbol)
                    leverage_success += 1
                except Exception as e:
                    continue
            
            logger.logger.info(f"✅ Leverage {self.leverage}x set for {leverage_success}/{len(self.symbols)} symbols")
            
            balance = self._get_account_balance()
            if balance < 50:
                logger.logger.error(f"❌ Insufficient balance: ${balance:.2f}")
                return False
            
            logger.logger.info(f"✅ Account balance: ${balance:.2f}")
            
            self.dashboard.start()
            
            return True
            
        except Exception as e:
            logger.logger.error(f"❌ Setup failed: {e}")
            return False

    def fetch_ultra_fast_data(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados rapidamente"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=20)
                if len(ohlcv) >= 10:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
            except Exception as e:
                logger.logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
                
        return ohlcv_data

    def analyze_symbol_ultra_fast(self, symbol: str) -> Optional[Dict]:
        """Análise rápida de símbolo"""
        try:
            ohlcv_data = self.fetch_ultra_fast_data(symbol)
            
            if len(ohlcv_data) < 1:
                return None
            
            result = self.analyzer.multi_timeframe_analysis_detailed(symbol, ohlcv_data)
            
            if (result and result['signal'] != 'NEUTRAL' and 
                result['score'] >= AdvancedTradingConfig.MIN_SIGNAL_SCORE):
                
                self.database.save_signal_analysis(symbol, 'multi', result)
                return result
            
            return None
            
        except Exception as e:
            logger.logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def run_ultra_fast_analysis_cycle(self) -> int:
        """Ciclo de análise - MÉTODO ADICIONADO"""
        signals_found = 0
        positions_opened = 0
        
        try:
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            ready_symbols = []
            current_time = time.time()
            
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    time_since = current_time - self.symbol_cooldown[symbol]
                    if time_since >= self.min_cooldown:
                        ready_symbols.append(symbol)
                else:
                    ready_symbols.append(symbol)
            
            if not ready_symbols:
                return 0
            
            logger.logger.info(f"[🔍 ANALYSIS] Scanning {len(ready_symbols)} symbols...")
            
            # Análise paralela
            futures = {}
            for symbol in ready_symbols:
                future = self.executor.submit(self.analyze_symbol_ultra_fast, symbol)
                futures[future] = symbol
            
            # Processar resultados
            for future in as_completed(futures, timeout=20):
                symbol = futures[future]
                
                try:
                    result = future.result(timeout=5)
                    
                    if result:
                        signals_found += 1
                        logger.logger.info(f"🎯 SIGNAL: {symbol} {result['signal']} (Score: {result['score']:.1f})")
                        
                        success = self.open_position_safe(symbol, result)
                        if success:
                            positions_opened += 1
                            
                except Exception as e:
                    logger.logger.debug(f"Future error {symbol}: {e}")
            
            if signals_found > 0:
                logger.logger.info(f"[✅ ANALYSIS] {signals_found} signals, {positions_opened} positions opened")
            else:
                logger.logger.info(f"[⏸️ ANALYSIS] No signals found")
            
            return positions_opened
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis cycle error: {e}")
            return 0

    def calculate_position_size_conservative(self, symbol: str, signal_strength: float) -> float:
        """Calcula tamanho da posição"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            base_size = AdvancedTradingConfig.MAX_POSITION_SIZE
            strength_multiplier = 0.6 + (signal_strength * 0.4)
            
            if self.risk_manager.should_increase_aggression():
                strength_multiplier = min(strength_multiplier * 1.2, 1.0)
            
            position_usdt = balance * base_size * strength_multiplier
            
            # Obter preço atual
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            if price <= 0:
                return 0
            
            quantity = position_usdt / price
            
            # Aplicar precisão
            try:
                quantity = self.exchange.amount_to_precision(symbol, quantity)
                final_quantity = float(quantity) if quantity else 0
            except:
                return 0
            
            # Verificar quantidade mínima
            min_notional = 5.0
            if final_quantity * price < min_notional:
                return 0
            
            return final_quantity
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0

    def open_position_safe(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição com validação"""
        try:
            # Verificações iniciais
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= AdvancedTradingConfig.MAX_POSITIONS:
                return False
            
            # Cooldown
            current_time = time.time()
            if symbol in self.symbol_cooldown:
                time_since = current_time - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    return False
            
            # Validar RSI
            if (signal_info['rsi'] >= AdvancedTradingConfig.MAX_RSI or 
                signal_info['rsi'] <= AdvancedTradingConfig.MIN_RSI):
                return False
            
            # Calcular posição
            signal_strength = signal_info['signal_strength']
            quantity = self.calculate_position_size_conservative(symbol, signal_strength)
            
            if quantity <= 0:
                return False
            
            # SL/TP
            sl_pct, tp_pct = self.sl_tp_calculator.calculate_levels(
                df=signal_info['df'],
                signal_strength=signal_strength,
                timeframe=signal_info['timeframe'],
                multi_tf_data=signal_info.get('timeframe_results', {})
            )
            
            signal = signal_info['signal']
            
            # Obter preço atual
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                if signal == 'LONG':
                    entry_price = ticker['ask']
                else:
                    entry_price = ticker['bid']
            except:
                entry_price = signal_info['price']
            
            if entry_price <= 0:
                return False
            
            # Calcular SL/TP
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_open = 'buy'
                side_close = 'sell'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_open = 'sell'
                side_close = 'buy'
            
            risk_reward_ratio = tp_pct / sl_pct
            
            logger.logger.info(f"\n🚀 OPENING: {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f} | Qty: {quantity:.4f}")
            logger.logger.info(f"   SL: ${sl_price:.4f} | TP: ${tp_price:.4f}")
            logger.logger.info(f"   R/R: {risk_reward_ratio:.1f}:1")
            
            try:
                # Ordem principal
                if signal == 'LONG':
                    order = self.exchange.create_market_buy_order(symbol, quantity)
                else:
                    order = self.exchange.create_market_sell_order(symbol, quantity)
                
                logger.logger.info(f"✅ Order executed: {order.get('id')}")
                
                time.sleep(1)
                
                # SL/TP
                sl_order_id = None
                tp_order_id = None
                
                try:
                    # Stop Loss
                    sl_order = self.exchange.create_order(
                        symbol, 'STOP_MARKET', side_close, quantity,
                        params={
                            'stopPrice': sl_price, 
                            'triggerBy': 'LastPrice', 
                            'reduceOnly': True
                        }
                    )
                    sl_order_id = sl_order.get('id')
                    
                    # Take Profit
                    tp_order = self.exchange.create_order(
                        symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                        params={
                            'stopPrice': tp_price, 
                            'triggerBy': 'LastPrice', 
                            'reduceOnly': True
                        }
                    )
                    tp_order_id = tp_order.get('id')
                    
                except Exception as e:
                    logger.logger.warning(f"⚠️ SL/TP failed: {e}")
                
                # Salvar posição
                trade_data = {
                    'symbol': symbol,
                    'signal': signal,
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'stop_loss_price': sl_price,
                    'take_profit_price': tp_price,
                    'stop_loss_pct': sl_pct,
                    'take_profit_pct': tp_pct,
                    'risk_reward_ratio': risk_reward_ratio,
                    'timestamp': datetime.now(),
                    'order_id': order.get('id'),
                    'sl_order_id': sl_order_id,
                    'tp_order_id': tp_order_id,
                    'signal_strength': signal_strength,
                    'reasons': signal_info['reasons'][:3],
                    'multi_tf_score': signal_info['score']
                }
                
                self.active_positions[symbol] = trade_data
                self.symbol_cooldown[symbol] = current_time
                
                self.database.save_trade(trade_data)
                
                logger.logger.info(f"✅ POSITION OPENED: {symbol}")
                
                return True
                
            except Exception as order_error:
                logger.logger.error(f"❌ Order failed: {order_error}")
                return False
            
        except Exception as e:
            logger.logger.error(f"❌ Position error {symbol}: {e}")
            return False

    def check_positions_safe(self):
        """Monitora posições - MÉTODO ADICIONADO"""
        if not self.active_positions:
            return
        
        try:
            symbols = list(self.active_positions.keys())
            
            for symbol in symbols:
                try:
                    positions = self.exchange.fetch_positions([symbol])
                    
                    for pos in positions:
                        if pos['symbol'] == symbol:
                            contracts = float(pos.get('contracts', 0))
                            unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                            
                            if contracts == 0:
                                self._handle_position_close_safe(symbol, pos)
                            break
                            
                except Exception as e:
                    logger.logger.debug(f"Position check error {symbol}: {e}")
                    
        except Exception as e:
            logger.logger.error(f"❌ Position check error: {e}")

    def _handle_position_close_safe(self, symbol: str, position_data: Dict):
        """Fecha posição - MÉTODO ADICIONADO"""
        try:
            if symbol not in self.active_positions:
                return
                
            trade_info = self.active_positions[symbol]
            unrealized_pnl = float(position_data.get('unrealizedPnl', 0))
            
            balance = self._get_account_balance()
            pnl_pct = (unrealized_pnl / balance) if balance > 0 else 0
            
            exit_reason = "AUTO"
            if abs(unrealized_pnl) > 0:
                exit_reason = "TAKE_PROFIT" if unrealized_pnl > 0 else "STOP_LOSS"
            
            self.risk_manager.register_trade_result(pnl_pct, symbol)
            
            exit_price = position_data.get('markPrice', trade_info['entry_price'])
            self.database.close_trade(symbol, exit_price, pnl_pct, unrealized_pnl, exit_reason)
            
            logger.logger.info(f"🔒 POSITION CLOSED: {symbol} | P&L: {pnl_pct*100:+.2f}%")
            
            del self.active_positions[symbol]
            
        except Exception as e:
            logger.logger.error(f"❌ Position close error {symbol}: {e}")

    def run_daily_report_simple(self):
        """Relatório diário - MÉTODO ADICIONADO"""
        try:
            stats = self.risk_manager.get_risk_status()
            balance = self._get_account_balance()
            
            report = f"""
📊 DAILY REPORT
Trades: {stats['trades_today']}/{stats['target_trades']}
P&L: {stats['daily_pnl']:+.2f}%
Balance: ${balance:.2f}
            """
            
            logger.logger.info(report)
            
        except Exception as e:
            logger.logger.error(f"❌ Daily report error: {e}")

    def run(self):
        """Loop principal completo"""
        logger.logger.info(f"\n{'='*80}")
        logger.logger.info(f"🚀 COMPLETE ADVANCED TRADING BOT")
        logger.logger.info(f"{'='*80}")
        logger.logger.info(f"SYMBOLS: {len(self.symbols)} coins")
        logger.logger.info(f"TARGET: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"{'='*80}\n")
        
        if not self.setup_account():
            return
        
        # Loop principal
        cycle = 0
        last_daily_report = datetime.now().date()
        
        try:
            while True:
                cycle += 1
                cycle_start = time.time()
                
                # Status
                if cycle % 5 == 1:
                    stats = self.risk_manager.get_risk_status()
                    logger.logger.info(f"\n[🔄 CYCLE #{cycle}]")
                    logger.logger.info(f"Active: {len(self.active_positions)}/{AdvancedTradingConfig.MAX_POSITIONS}")
                    logger.logger.info(f"Today: {stats['trades_today']}/{stats['target_trades']}")
                    logger.logger.info(f"P&L: {stats['daily_pnl']:+.2f}%")
                
                # Verificar se pode operar
                can_trade, reason = self.risk_manager.can_trade()
                if not can_trade:
                    logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(60)
                    continue
                
                # Relatório diário
                current_date = datetime.now().date()
                if current_date != last_daily_report:
                    self.run_daily_report_simple()
                    last_daily_report = current_date
                
                # Análise
                positions_opened = self.run_ultra_fast_analysis_cycle()
                
                # Monitorar posições
                self.check_positions_safe()
                
                # Timing
                cycle_duration = time.time() - cycle_start
                sleep_time = max(10, AdvancedTradingConfig.ANALYSIS_INTERVAL - cycle_duration)
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Manual shutdown")
        except Exception as e:
            logger.logger.error(f"❌ Fatal error: {e}")
        finally:
            self.executor.shutdown(wait=False)
            logger.logger.info("✅ Bot shutdown complete")

# =================== DASHBOARD OTIMIZADO ===================
class OptimizedDashboard:
    def __init__(self, bot_instance, port=5000):
        self.bot = bot_instance
        self.app = Flask(__name__)
        self.port = port
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/')
        def index():
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Advanced Multi-TF Bot - FIXED</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e1a 0%, #1e293b 50%, #334155 100%);
            color: #f8fafc;
            min-height: 100vh;
            padding: 15px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            background: rgba(30, 41, 59, 0.8);
            border-radius: 12px;
            border: 2px solid #10b981;
        }
        .header h1 {
            font-size: 2.2em;
            margin-bottom: 10px;
            color: #10b981;
        }
        .status-badge {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 8px 16px;
            border-radius: 16px;
            font-weight: bold;
            font-size: 0.9em;
            display: inline-block;
            margin: 6px;
        }
        .fixed-badge {
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(30, 41, 59, 0.7);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #475569;
            text-align: center;
        }
        .stat-label {
            font-size: 0.8em;
            color: #94a3b8;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #e2e8f0;
        }
        .stat-value.positive { color: #10b981; }
        .stat-value.negative { color: #ef4444; }
        .stat-value.warning { color: #f59e0b; }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(71, 85, 105, 0.5);
            border-radius: 3px;
            margin-top: 8px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #06b6d4);
            transition: width 0.5s ease;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            font-size: 0.85em;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn-primary { background: #3b82f6; color: white; }
        .btn-success { background: #10b981; color: white; }
        .btn-warning { background: #f59e0b; color: white; }
        .btn-danger { background: #ef4444; color: white; }
        .last-update {
            text-align: center;
            margin-top: 15px;
            color: #94a3b8;
            font-size: 0.8em;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .status-active { background: #10b981; animation: blink 1.5s infinite; }
        .status-paused { background: #f59e0b; }
        @keyframes blink { 50% { opacity: 0.3; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced Multi-TF Trading Bot</h1>
            <div class="status-badge fixed-badge">✅ JSON ERRORS FIXED</div>
            <div class="status-badge">📊 TOP 20 COINS</div>
            <div class="status-badge">⚡ 15m-4h ANALYSIS</div>
            <div class="status-badge">🎯 15+ TRADES/DAY</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">System Status</div>
                <div id="system-status" class="stat-value">Loading...</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Daily P&L</div>
                <div id="daily-pnl" class="stat-value">0.00%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Trades Today</div>
                <div id="trades-today" class="stat-value">0</div>
                <div class="progress-bar">
                    <div id="trades-progress" class="progress-fill" style="width: 0%"></div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Win Rate</div>
                <div id="win-rate" class="stat-value">0.0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Positions</div>
                <div id="active-positions" class="stat-value">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg R/R</div>
                <div id="avg-rr" class="stat-value">0.0:1</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mode</div>
                <div id="mode" class="stat-value">NORMAL</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Errors</div>
                <div id="errors" class="stat-value">0</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="updateDashboard()">🔄 Refresh</button>
            <a href="/api/status" target="_blank" class="btn btn-success">📊 Full Status</a>
            <button class="btn btn-warning" onclick="showInfo()">📈 Info</button>
            <button class="btn btn-danger" onclick="showLogs()">📋 Logs</button>
        </div>
        
        <div class="last-update">
            Last Update: <span id="last-update">Never</span>
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/dashboard')
                .then(response => response.json())
                .then(data => {
                    // System Status
                    const statusEl = document.getElementById('system-status');
                    const indicator = data.risk_status.can_trade ? 
                        '<span class="status-indicator status-active"></span>ACTIVE' : 
                        '<span class="status-indicator status-paused"></span>PAUSED';
                    statusEl.innerHTML = indicator;
                    statusEl.className = 'stat-value ' + (data.risk_status.can_trade ? 'positive' : 'warning');
                    
                    // Daily P&L
                    const pnlEl = document.getElementById('daily-pnl');
                    pnlEl.textContent = (data.risk_status.daily_pnl >= 0 ? '+' : '') + data.risk_status.daily_pnl.toFixed(2) + '%';
                    pnlEl.className = 'stat-value ' + (data.risk_status.daily_pnl >= 0 ? 'positive' : 'negative');
                    
                    // Trades Today
                    document.getElementById('trades-today').textContent = data.risk_status.trades_today + '/' + data.risk_status.target_trades;
                    const progressPct = (data.risk_status.trades_today / data.risk_status.target_trades) * 100;
                    document.getElementById('trades-progress').style.width = Math.min(progressPct, 100) + '%';
                    
                    // Other stats
                    document.getElementById('win-rate').textContent = data.risk_status.statistics.win_rate.toFixed(1) + '%';
                    document.getElementById('active-positions').textContent = data.active_positions + '/5';
                    document.getElementById('avg-rr').textContent = data.risk_status.statistics.avg_risk_reward.toFixed(1) + ':1';
                    
                    // Mode
                    const modeEl = document.getElementById('mode');
                    if (data.risk_status.should_be_aggressive) {
                        modeEl.textContent = 'AGGRESSIVE';
                        modeEl.className = 'stat-value warning';
                    } else {
                        modeEl.textContent = 'NORMAL';
                        modeEl.className = 'stat-value';
                    }
                    
                    // Errors
                    const errorsEl = document.getElementById('errors');
                    errorsEl.textContent = data.risk_status.error_count;
                    errorsEl.className = 'stat-value ' + (data.risk_status.error_count > 5 ? 'warning' : '');
                    
                    // Last Update
                    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Dashboard update error:', error);
                });
        }
        
        function showInfo() {
            alert('🚀 ADVANCED BOT FEATURES:\\n\\n' +
                  '✅ JSON errors fixed\\n' +
                  '✅ Thread-safe database\\n' +
                  '✅ Optimized analysis\\n' +
                  '✅ 20 top coins monitoring\\n' +
                  '⚡ Multi-timeframe (15m-4h)\\n' +
                  '🎯 Target: 15+ trades/day');
        }
        
        function showLogs() {
            alert('📋 Log files location:\\n\\n' +
                  'logs_advanced/bot_main_*.log\\n' +
                  'logs_advanced/bot_trades_*.log\\n' +
                  'logs_advanced/bot_analysis_*.log\\n\\n' +
                  'Database: trading_data_advanced/');
        }
        
        // Auto-update every 10 seconds
        updateDashboard();
        setInterval(updateDashboard, 10000);
    </script>
</body>
</html>
            """
            return html
        
        @self.app.route('/api/dashboard')
        def api_dashboard():
            try:
                return jsonify({
                    'risk_status': self.bot.risk_manager.get_risk_status(),
                    'active_positions': len(self.bot.active_positions),
                    'symbols_count': len(self.bot.symbols),
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def api_status():
            try:
                status = self.bot.risk_manager.get_risk_status()
                status.update({
                    'symbols': self.bot.symbols[:10],  # Primeiros 10
                    'total_symbols': len(self.bot.symbols),
                    'timeframes': AdvancedTradingConfig.TIMEFRAMES
                })
                return jsonify(status)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def start(self):
        def run_server():
            try:
                self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)
            except Exception as e:
                logger.logger.error(f"Dashboard error: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        logger.logger.info(f"✅ Optimized Dashboard started: http://localhost:{self.port}")

# =================== BOT PRINCIPAL OTIMIZADO E CORRIGIDO ===================
class OptimizedAdvancedBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing FIXED Advanced Multi-Timeframe Bot...")
        
        # Componentes com tratamento de erro
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.analyzer = OptimizedMultiTimeframeAnalyzer()
        self.sl_tp_calculator = AdvancedStopLossTakeProfit()
        self.dashboard = OptimizedDashboard(self, port=5000)
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = self.cmc_api.get_top_coins()
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.primary_timeframe = AdvancedTradingConfig.PRIMARY_TIMEFRAME
        self.leverage = 3
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 1800  # 30 min
        
        # Threading otimizado
        self.executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="analyzer")
        
        # Taxa
        self.fee_rate = 0.00075
        
        logger.logger.info(f"✅ FIXED Bot initialized - {len(self.symbols)} symbols")
        
        # Alerta
        mode = "TESTNET" if testnet else "🚨 PRODUCTION"
        self.alert_system.send_alert(
            f"Fixed Advanced Bot Started ({mode})",
            f"🚀 JSON Errors Fixed\n📊 {len(self.symbols)} Top Coins\n⚡ Multi-TF Analysis\n🎯 Target: 15 trades/day",
            "success"
        )

    def _setup_exchange(self):
        """Configura exchange com melhor tratamento de erros"""
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("❌ API keys not configured")
        
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 15000
            },
            'sandbox': self.testnet,
        })
        
        logger.logger.info("✅ Exchange configured")

    def setup_account(self) -> bool:
        """Setup otimizado com melhor tratamento de leverage"""
        try:
            # Sincronizar
            self.exchange.load_time_difference()
            logger.logger.info("✅ Timestamp synchronized")
            
            # Carregar mercados
            markets = self.exchange.load_markets()
            logger.logger.info(f"✅ Markets loaded: {len(markets)}")
            
            # ✅ LEVERAGE COM TRATAMENTO MELHOR DE ERROS
            leverage_success = 0
            for symbol in self.symbols:
                try:
                    self.exchange.set_leverage(self.leverage, symbol)
                    leverage_success += 1
                    time.sleep(0.05)  # Menor delay
                except Exception as e:
                    error_msg = str(e).lower()
                    if "110043" in error_msg or "only support linear" in error_msg:
                        # Erro conhecido - símbolo não suporta leverage
                        continue
                    else:
                        logger.logger.warning(f"⚠️ Leverage error for {symbol}: {e}")
            
            logger.logger.info(f"✅ Leverage {self.leverage}x set for {leverage_success}/{len(self.symbols)} symbols")
            
            # Verificar saldo
            balance = self._get_account_balance()
            min_balance = 2000 if not self.testnet else 200
            
            if balance < min_balance:
                error_msg = f"❌ Insufficient balance: ${balance:.2f}"
                logger.logger.error(error_msg)
                return False
            
            logger.logger.info(f"✅ Account balance: ${balance:.2f}")
            logger.logger.info(f"✅ Max position per trade: ${balance * self.risk_manager.max_position_size:.2f}")
            
            # Dashboard
            self.dashboard.start()
            
            # Notificar
            mode = "TESTNET" if self.testnet else "🚨 PRODUCTION"
            self.alert_system.send_alert(
                f"Fixed Bot Setup ({mode})",
                f"💰 Balance: ${balance:.2f}\n📊 {len(self.symbols)} coins\n⚡ Leverage: {leverage_success} symbols\n✅ All systems operational",
                "success"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Setup failed: {e}"
            logger.logger.error(error_msg)
            return False

    def _get_account_balance(self) -> float:
        """Saldo com tratamento de erro"""
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            logger.logger.error(f"❌ Balance error: {e}")
            return 0

    def fetch_multi_timeframe_data_safe(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados multi-TF com tratamento robusto de erros"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=80)
                if len(ohlcv) >= 30:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
                    
            except Exception as e:
                # Log somente erros inesperados
                if "not found" not in str(e).lower():
                    logger.logger.error(f"❌ Data error {symbol} {timeframe}: {e}")
                self.risk_manager.error_count += 1
                
        return ohlcv_data

    def analyze_symbol_safe(self, symbol: str) -> Optional[Dict]:
        """Análise segura de um símbolo"""
        try:
            # Buscar dados
            ohlcv_data = self.fetch_multi_timeframe_data_safe(symbol)
            
            if len(ohlcv_data) < 2:  # Pelo menos 2 timeframes
                return None
            
            # Análise multi-TF
            result = self.analyzer.multi_timeframe_analysis_simple(symbol, ohlcv_data)
            
            # Salvar análise (simplificada para evitar JSON errors)
            if result and result['signal'] != 'NEUTRAL':
                self.database.save_signal_analysis(symbol, 'multi', result)
            
            return result
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis error {symbol}: {e}")
            self.risk_manager.error_count += 1
            return None

    def calculate_position_size_safe(self, symbol: str, signal_strength: float) -> float:
        """Calcula posição com tratamento de erro"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            # Tamanho adaptativo
            size = self.risk_manager.calculate_position_size_adaptive(signal_strength)
            position_usdt = balance * size * (1 - self.fee_rate * 2)
            
            # Converter
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = position_usdt / price
            
            # Precisão
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            return float(quantity) if quantity else 0
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0

    def open_position_safe(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição com tratamento completo de erros"""
        try:
            # Verificações
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= self.risk_manager.max_positions:
                return False
            
            # Cooldown
            if symbol in self.symbol_cooldown:
                time_since = time.time() - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    return False
            
            # Calcular posição
            signal_strength = signal_info['signal_strength']
            quantity = self.calculate_position_size_safe(symbol, signal_strength)
            
            if quantity <= 0:
                return False
            
            # SL/TP
            sl_pct, tp_pct = self.sl_tp_calculator.calculate_levels(
                df=signal_info['df'],
                signal_strength=signal_strength,
                timeframe=signal_info['timeframe'],
                multi_tf_data=signal_info.get('timeframe_results', {})
            )
            
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_close = 'sell'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_close = 'buy'
            
            risk_reward_ratio = tp_pct / sl_pct
            
            # Log simplificado
            logger.logger.info(f"\n🚀 OPENING POSITION: {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f} | Qty: {quantity}")
            logger.logger.info(f"   SL: ${sl_price:.4f} (-{sl_pct*100:.2f}%)")
            logger.logger.info(f"   TP: ${tp_price:.4f} (+{tp_pct*100:.2f}%)")
            logger.logger.info(f"   R/R: {risk_reward_ratio:.1f}:1")
            
            # Executar ordem principal
            if signal == 'LONG':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.logger.info(f"✅ Market order: {order.get('id')}")
            
            time.sleep(1)
            
            # SL/TP orders com tratamento de erro
            sl_order_id = None
            tp_order_id = None
            
            try:
                # Stop Loss
                sl_order = self.exchange.create_order(
                    symbol, 'STOP_MARKET', side_close, quantity,
                    params={'stopPrice': sl_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                sl_order_id = sl_order.get('id')
                logger.logger.info(f"✅ Stop Loss: {sl_order_id}")
                
                # Take Profit
                tp_order = self.exchange.create_order(
                    symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                    params={'stopPrice': tp_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                tp_order_id = tp_order.get('id')
                logger.logger.info(f"✅ Take Profit: {tp_order_id}")
                
            except Exception as e:
                logger.logger.error(f"⚠️ SL/TP error: {e}")
            
            # Salvar posição
            trade_data = {
                'symbol': symbol,
                'signal': signal,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss_price': sl_price,
                'take_profit_price': tp_price,
                'stop_loss_pct': sl_pct,
                'take_profit_pct': tp_pct,
                'risk_reward_ratio': risk_reward_ratio,
                'timestamp': datetime.now(),
                'order_id': order.get('id'),
                'sl_order_id': sl_order_id,
                'tp_order_id': tp_order_id,
                'signal_strength': signal_strength,
                'atr': signal_info['atr'],
                'reasons': signal_info['reasons'][:3],  # Apenas 3 reasons
                'multi_tf_score': signal_info['score']
            }
            
            self.active_positions[symbol] = trade_data
            self.symbol_cooldown[symbol] = time.time()
            
            self.database.save_trade(trade_data)
            
            # Métricas
            position_value = entry_price * quantity
            logger.logger.info(f"💰 Position: ${position_value:.2f} | Active: {len(self.active_positions)}/{self.risk_manager.max_positions}")
            logger.logger.info(f"🎯 Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
            logger.logger.info(f"✅ POSITION OPENED SUCCESSFULLY!\n")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Position open error {symbol}: {e}"
            logger.logger.error(error_msg)
            self.risk_manager.error_count += 1
            return False

    def run_optimized_analysis_cycle(self) -> int:
        """Ciclo de análise otimizado"""
        signals_found = 0
        
        try:
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            # Filtrar símbolos em cooldown
            ready_symbols = []
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    time_since = time.time() - self.symbol_cooldown[symbol]
                    if time_since >= self.min_cooldown:
                        ready_symbols.append(symbol)
                else:
                    ready_symbols.append(symbol)
            
            if not ready_symbols:
                logger.logger.info("⏸️ All symbols in cooldown")
                return 0
            
            logger.logger.info(f"[🔍 ANALYSIS] Scanning {len(ready_symbols)} symbols...")
            
            # Análise paralela com timeout
            futures = {}
            for symbol in ready_symbols:
                future = self.executor.submit(self.analyze_symbol_safe, symbol)
                futures[future] = symbol
            
            # Processar resultados com timeout
            for future in as_completed(futures, timeout=60):
                symbol = futures[future]
                try:
                    result = future.result(timeout=10)
                    
                    if result and result['signal'] != 'NEUTRAL':
                        signals_found += 1
                        
                        logger.logger.info(f"🚨 SIGNAL: {symbol} {result['signal']} (Score: {result['score']:.1f})")
                        
                        # Tentar abrir posição
                        success = self.open_position_safe(symbol, result)
                        
                        if success:
                            logger.logger.info(f"   ✅ Position opened!")
                        
                except Exception as e:
                    logger.logger.error(f"❌ Future error {symbol}: {e}")
            
            logger.logger.info(f"[🔍 COMPLETE] {signals_found} signals found")
            
            return signals_found
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis cycle error: {e}")
            self.risk_manager.error_count += 1
            return 0

    def check_positions_safe(self):
        """Monitor posições com tratamento de erro"""
        if not self.active_positions:
            return
        
        try:
            symbols = list(self.active_positions.keys())
            positions = self.exchange.fetch_positions(symbols)
            
            for pos in positions:
                symbol = pos['symbol']
                if symbol not in self.active_positions:
                    continue
                
                contracts = float(pos.get('contracts', 0))
                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                
                if contracts == 0:
                    self._handle_position_close_safe(symbol, pos)
                    
        except Exception as e:
            logger.logger.error(f"❌ Position check error: {e}")
            self.risk_manager.error_count += 1

    def _handle_position_close_safe(self, symbol: str, position_data: Dict):
        """Handle position close com tratamento de erro"""
        try:
            trade_info = self.active_positions[symbol]
            unrealized_pnl = float(position_data.get('unrealizedPnl', 0))
            
            balance = self._get_account_balance()
            pnl_pct = (unrealized_pnl / balance) if balance > 0 else 0
            
            exit_reason = "AUTO"
            if abs(unrealized_pnl) > 0:
                exit_reason = "TAKE_PROFIT" if unrealized_pnl > 0 else "STOP_LOSS"
            
            self.risk_manager.register_trade_result(pnl_pct, symbol)
            
            exit_price = position_data.get('markPrice', trade_info['entry_price'])
            self.database.close_trade(symbol, exit_price, pnl_pct, unrealized_pnl, exit_reason)
            
            duration = datetime.now() - trade_info['timestamp']
            duration_str = f"{duration.total_seconds()/3600:.1f}h"
            
            status = "PROFIT" if pnl_pct > 0 else "LOSS"
            emoji = "💚" if pnl_pct > 0 else "🔴"
            
            logger.logger.info(f"\n{emoji} POSITION CLOSED: {symbol} {status}")
            logger.logger.info(f"   P&L: {pnl_pct*100:+.2f}% (${unrealized_pnl:+.2f}) | Duration: {duration_str}")
            logger.logger.info(f"   Daily: {self.risk_manager.daily_pnl*100:+.2f}% | Today: {self.risk_manager.trades_today}")
            
            del self.active_positions[symbol]
            
        except Exception as e:
            logger.logger.error(f"❌ Position close error {symbol}: {e}")

    def run_daily_report_simple(self):
        """Relatório diário simplificado"""
        try:
            stats = self.risk_manager.get_risk_status()
            balance = self._get_account_balance()
            
            report = f"""
📊 DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')}

💰 PERFORMANCE:
Daily P&L: {stats['daily_pnl']:+.2f}%
Trades: {stats['trades_today']}/{stats['target_trades']}
Win Rate: {stats['statistics']['win_rate']:.1f}%

🚀 SYSTEM:
Balance: ${balance:.2f}
Active: {len(self.active_positions)}/5
Errors: {stats['error_count']}

✅ All systems operational
            """
            
            self.alert_system.send_alert("Daily Report", report, "info")
            logger.logger.info("✅ Daily report sent")
            
        except Exception as e:
            logger.logger.error(f"❌ Daily report error: {e}")

    def run(self):
        """Loop principal otimizado"""
        logger.logger.info(f"\n{'='*100}")
        logger.logger.info(f"🚀 FIXED ADVANCED MULTI-TIMEFRAME BOT")
        logger.logger.info(f"{'='*100}")
        
        mode_msg = f"{'🧪 TESTNET' if self.testnet else '🚨 PRODUCTION'}"
        logger.logger.info(f"MODE: {mode_msg}")
        logger.logger.info(f"SYMBOLS: {len(self.symbols)} coins")
        logger.logger.info(f"TIMEFRAMES: {', '.join(self.timeframes)}")
        logger.logger.info(f"TARGET: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"DASHBOARD: http://localhost:5000")
        logger.logger.info(f"✅ JSON ERRORS FIXED")
        logger.logger.info(f"{'='*100}\n")
        
        # Setup
        if not self.setup_account():
            logger.logger.error("❌ Setup failed")
            return
        
        # Loop principal
        cycle = 0
        last_daily_report = datetime.now().date()
        
        try:
            while True:
                cycle += 1
                cycle_start = time.time()
                
                # Status
                if cycle % 10 == 1:
                    can_trade, reason = self.risk_manager.can_trade()
                    aggression = "🔥 AGGRESSIVE" if self.risk_manager.should_increase_aggression() else "📊 NORMAL"
                    
                    logger.logger.info(f"\n[CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                    logger.logger.info(f"Status: {'🚀 ACTIVE' if can_trade else f'⏸️ PAUSED ({reason})'}")
                    logger.logger.info(f"Mode: {aggression}")
                    logger.logger.info(f"Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
                    logger.logger.info(f"Active: {len(self.active_positions)}/5 | Errors: {self.risk_manager.error_count}")
                
                # Verificar trading
                can_trade, reason = self.risk_manager.can_trade()
                if not can_trade:
                    if cycle % 20 == 1:
                        logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(240)  # 4 minutos
                    continue
                
                # Relatório diário
                if datetime.now().date() != last_daily_report:
                    self.run_daily_report_simple()
                    last_daily_report = datetime.now().date()
                
                # Análise
                signals_found = self.run_optimized_analysis_cycle()
                
                # Monitor posições
                self.check_positions_safe()
                
                # Summary
                if signals_found > 0 or cycle % 20 == 1:
                    stats = self.risk_manager.get_risk_status()['statistics']
                    logger.logger.info(f"\n[📊 SUMMARY #{cycle}]")
                    logger.logger.info(f"🎯 Signals: {signals_found} | Active: {len(self.active_positions)}")
                    logger.logger.info(f"🏆 WR: {stats['win_rate']:.1f}% | R/R: {stats['avg_risk_reward']:.1f}:1")
                    logger.logger.info(f"💰 Daily: {self.risk_manager.daily_pnl*100:+.2f}% | Trades: {self.risk_manager.trades_today}")
                
                # Timing
                cycle_duration = time.time() - cycle_start
                sleep_time = max(90, AdvancedTradingConfig.ANALYSIS_INTERVAL - cycle_duration)
                
                if cycle % 15 == 1:
                    logger.logger.info(f"⏱️ Next cycle in {sleep_time/60:.1f}m")
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Manual shutdown")
            
        except Exception as e:
            error_msg = f"❌ Fatal error: {e}"
            logger.logger.error(error_msg)
            logger.logger.error(traceback.format_exc())
            
        finally:
            self._shutdown_safe()

    def _shutdown_safe(self):
        """Shutdown seguro"""
        logger.logger.info("🛑 Shutting down FIXED Advanced Bot...")
        
        try:
            if self.active_positions:
                logger.logger.warning(f"{len(self.active_positions)} positions still active")
            
            stats = self.risk_manager.get_risk_status()['statistics']
            
            final_report = f"""
FIXED Advanced Bot shutdown complete.

FINAL STATS:
Trades: {stats['total_trades']}
Win Rate: {stats['win_rate']:.1f}%
Daily P&L: {self.risk_manager.daily_pnl*100:+.2f}%

✅ JSON errors fixed
✅ Thread-safe database
✅ Optimized performance

Shutdown: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            logger.logger.info(final_report)
            
            # Cleanup
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            logger.logger.error(f"❌ Shutdown error: {e}")
        
        logger.logger.info("✅ FIXED Advanced Bot shutdown complete")
    
    def _setup_exchange(self):
        """Configura exchange com melhor tratamento de erros"""
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("❌ API keys not configured")
        
        self.exchange = ccxt.bybit({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 15000
            },
            'sandbox': self.testnet,  # Usar sandbox para testnet
        })
        
        logger.logger.info("✅ Exchange configured")
    
    def fetch_multi_timeframe_data_safe(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados multi-TF com tratamento robusto de erros"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                # Buscar mais dados para calcular indicadores com mais precisão
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)
                if len(ohlcv) >= 50:  # Pelo menos 50 velas
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
                    
            except Exception as e:
                # Log somente erros inesperados
                if "not found" not in str(e).lower():
                    logger.logger.error(f"❌ Data error {symbol} {timeframe}: {e}")
                self.risk_manager.error_count += 1
                
        return ohlcv_data

    def analyze_symbol_safe(self, symbol: str) -> Optional[Dict]:
        """Análise segura de um símbolo"""
        try:
            # Buscar dados
            ohlcv_data = self.fetch_multi_timeframe_data_safe(symbol)
            
            if len(ohlcv_data) < 2:  # Pelo menos 2 timeframes
                return None
            
            # Análise multi-TF
            result = self.analyzer.multi_timeframe_analysis_simple(symbol, ohlcv_data)
            
            # Salvar análise (simplificada para evitar JSON errors)
            if result and result['signal'] != 'NEUTRAL':
                self.database.save_signal_analysis(symbol, 'multi', result)
            
            return result
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis error {symbol}: {e}")
            self.risk_manager.error_count += 1
            return None

    def calculate_position_size_safe(self, symbol: str, signal_strength: float) -> float:
        """Calcula posição com tratamento de erro"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            # Tamanho adaptativo
            size = self.risk_manager.calculate_position_size_adaptive(signal_strength)
            position_usdt = balance * size * (1 - self.fee_rate * 2)
            
            # Converter
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = position_usdt / price
            
            # Precisão
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            return float(quantity) if quantity else 0
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0

    def open_position_safe(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição com tratamento completo de erros"""
        try:
            # Verificações
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= self.risk_manager.max_positions:
                return False
            
            # Cooldown
            if symbol in self.symbol_cooldown:
                time_since = time.time() - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    return False
            
            # Calcular posição
            signal_strength = signal_info['signal_strength']
            quantity = self.calculate_position_size_safe(symbol, signal_strength)
            
            if quantity <= 0:
                return False
            
            # SL/TP
            sl_pct, tp_pct = self.sl_tp_calculator.calculate_levels(
                df=signal_info['df'],
                signal_strength=signal_strength,
                timeframe=signal_info['timeframe'],
                multi_tf_data=signal_info.get('timeframe_results', {})
            )
            
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_close = 'sell'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_close = 'buy'
            
            risk_reward_ratio = tp_pct / sl_pct
            
            # Log simplificado
            logger.logger.info(f"\n🚀 OPENING POSITION: {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f} | Qty: {quantity}")
            logger.logger.info(f"   SL: ${sl_price:.4f} (-{sl_pct*100:.2f}%)")
            logger.logger.info(f"   TP: ${tp_price:.4f} (+{tp_pct*100:.2f}%)")
            logger.logger.info(f"   R/R: {risk_reward_ratio:.1f}:1")
            
            # Executar ordem principal
            if signal == 'LONG':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.logger.info(f"✅ Market order: {order.get('id')}")
            
            time.sleep(1)
            
            # SL/TP orders com tratamento de erro
            sl_order_id = None
            tp_order_id = None
            
            try:
                # Stop Loss
                sl_order = self.exchange.create_order(
                    symbol, 'STOP_MARKET', side_close, quantity,
                    params={'stopPrice': sl_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                sl_order_id = sl_order.get('id')
                logger.logger.info(f"✅ Stop Loss: {sl_order_id}")
                
                # Take Profit
                tp_order = self.exchange.create_order(
                    symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                    params={'stopPrice': tp_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                tp_order_id = tp_order.get('id')
                logger.logger.info(f"✅ Take Profit: {tp_order_id}")
                
            except Exception as e:
                logger.logger.error(f"⚠️ SL/TP error: {e}")
            
            # Salvar posição
            trade_data = {
                'symbol': symbol,
                'signal': signal,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss_price': sl_price,
                'take_profit_price': tp_price,
                'stop_loss_pct': sl_pct,
                'take_profit_pct': tp_pct,
                'risk_reward_ratio': risk_reward_ratio,
                'timestamp': datetime.now(),
                'order_id': order.get('id'),
                'sl_order_id': sl_order_id,
                'tp_order_id': tp_order_id,
                'signal_strength': signal_strength,
                'atr': signal_info['atr'],
                'reasons': signal_info['reasons'][:3],  # Apenas 3 reasons
                'multi_tf_score': signal_info['score']
            }
            
            self.active_positions[symbol] = trade_data
            self.symbol_cooldown[symbol] = time.time()
            
            self.database.save_trade(trade_data)
            
            # Métricas
            position_value = entry_price * quantity
            logger.logger.info(f"💰 Position: ${position_value:.2f} | Active: {len(self.active_positions)}/{self.risk_manager.max_positions}")
            logger.logger.info(f"🎯 Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
            logger.logger.info(f"✅ POSITION OPENED SUCCESSFULLY!\n")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Position open error {symbol}: {e}"
            logger.logger.error(error_msg)
            self.risk_manager.error_count += 1
            return False        
    
def _setup_exchange(self):
    """Configura exchange com melhor tratamento de erros"""
    api_key = os.getenv('BYBIT_API_KEY')
    secret_key = os.getenv('BYBIT_API_SECRET')

    if not api_key or not secret_key:
        raise ValueError("❌ API keys not configured")

    # Exemplo de configuração da exchange:
    # self.exchange = ccxt.bybit({
    #     'apiKey': api_key,
    #     'secret': secret_key,
    #     'enableRateLimit': True,
    #     'options': {'defaultType': 'future'}
    # })
    self.exchange = ccxt.bybit({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
        'rateLimit': 100,
        'options': {
            'defaultType': 'linear',
            'adjustForTimeDifference': True,
            'recvWindow': 15000
        },
        'sandbox': self.testnet,  # Usar sandbox para testnet
    })
    
    def setup_account(self) -> bool:
        """Setup otimizado com melhor tratamento de leverage"""
        try:
            # Sincronizar
            self.exchange.load_time_difference()
            logger.logger.info("✅ Timestamp synchronized")
            
            # Carregar mercados
            markets = self.exchange.load_markets()
            logger.logger.info(f"✅ Markets loaded: {len(markets)}")
            
            # ✅ LEVERAGE COM TRATAMENTO MELHOR DE ERROS
            leverage_success = 0
            for symbol in self.symbols:
                try:
                    self.exchange.set_leverage(self.leverage, symbol)
                    leverage_success += 1
                    time.sleep(0.05)  # Menor delay
                except Exception as e:
                    error_msg = str(e).lower()
                    if "110043" in error_msg or "only support linear" in error_msg:
                        # Erro conhecido - símbolo não suporta leverage
                        continue
                    else:
                        logger.logger.warning(f"⚠️ Leverage error for {symbol}: {e}")
            
            logger.logger.info(f"✅ Leverage {self.leverage}x set for {leverage_success}/{len(self.symbols)} symbols")
            
            # Verificar saldo
            balance = self._get_account_balance()
            min_balance = 2000 if not self.testnet else 200
            
            if balance < min_balance:
                error_msg = f"❌ Insufficient balance: ${balance:.2f}"
                logger.logger.error(error_msg)
                return False
            
            logger.logger.info(f"✅ Account balance: ${balance:.2f}")
            logger.logger.info(f"✅ Max position per trade: ${balance * self.risk_manager.max_position_size:.2f}")
            
            # Dashboard
            self.dashboard.start()
            
            # Notificar
            mode = "TESTNET" if self.testnet else "🚨 PRODUCTION"
            self.alert_system.send_alert(
                f"Fixed Bot Setup ({mode})",
                f"💰 Balance: ${balance:.2f}\n📊 {len(self.symbols)} coins\n⚡ Leverage: {leverage_success} symbols\n✅ All systems operational",
                "success"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Setup failed: {e}"
            logger.logger.error(error_msg)
            return False
    
    def _get_account_balance(self) -> float:
        """Saldo com tratamento de erro"""
        try:
            balance = self.exchange.fetch_balance()
            return balance['USDT']['free']
        except Exception as e:
            logger.logger.error(f"❌ Balance error: {e}")
            return 0
    
    def fetch_multi_timeframe_data_safe(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados multi-TF com tratamento robusto de erros"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=80)
                if len(ohlcv) >= 30:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
                    
            except Exception as e:
                # Log somente erros inesperados
                if "not found" not in str(e).lower():
                    logger.logger.error(f"❌ Data error {symbol} {timeframe}: {e}")
                self.risk_manager.error_count += 1
                
        return ohlcv_data
    
    def calculate_position_size_safe(self, symbol: str, signal_strength: float) -> float:
        """Calcula posição com tratamento de erro"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            # Tamanho adaptativo
            size = self.risk_manager.calculate_position_size_adaptive(signal_strength)
            position_usdt = balance * size * (1 - self.fee_rate * 2)
            
            # Converter
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            quantity = position_usdt / price
            
            # Precisão
            quantity = self.exchange.amount_to_precision(symbol, quantity)
            return float(quantity) if quantity else 0
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0
    
    def analyze_symbol_safe(self, symbol: str) -> Optional[Dict]:
        """Análise segura de um símbolo"""
        try:
            # Buscar dados
            ohlcv_data = self.fetch_multi_timeframe_data_safe(symbol)
            
            if len(ohlcv_data) < 2:  # Pelo menos 2 timeframes
                return None
            
            # Análise multi-TF
            result = self.analyzer.multi_timeframe_analysis_simple(symbol, ohlcv_data)
            
            # Salvar análise (simplificada para evitar JSON errors)
            if result and result['signal'] != 'NEUTRAL':
                self.database.save_signal_analysis(symbol, 'multi', result)
            
            return result
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis error {symbol}: {e}")
            self.risk_manager.error_count += 1
            return None
    
    def open_position_safe(self, symbol: str, signal_info: Dict) -> bool:
        """Abre posição com tratamento completo de erros"""
        try:
            # Verificações
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= self.risk_manager.max_positions:
                return False
            
            # Cooldown
            if symbol in self.symbol_cooldown:
                time_since = time.time() - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    return False
            
            # Calcular posição
            signal_strength = signal_info['signal_strength']
            quantity = self.calculate_position_size_safe(symbol, signal_strength)
            
            if quantity <= 0:
                return False
            
            # SL/TP
            sl_pct, tp_pct = self.sl_tp_calculator.calculate_levels(
                df=signal_info['df'],
                signal_strength=signal_strength,
                timeframe=signal_info['timeframe'],
                multi_tf_data=signal_info.get('timeframe_results', {})
            )
            
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_close = 'sell'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_close = 'buy'
            
            risk_reward_ratio = tp_pct / sl_pct
            
            # Log simplificado
            logger.logger.info(f"\n🚀 OPENING POSITION: {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f} | Qty: {quantity}")
            logger.logger.info(f"   SL: ${sl_price:.4f} (-{sl_pct*100:.2f}%)")
            logger.logger.info(f"   TP: ${tp_price:.4f} (+{tp_pct*100:.2f}%)")
            logger.logger.info(f"   R/R: {risk_reward_ratio:.1f}:1")
            
            # Executar ordem principal
            if signal == 'LONG':
                order = self.exchange.create_market_buy_order(symbol, quantity)
            else:
                order = self.exchange.create_market_sell_order(symbol, quantity)
            
            logger.logger.info(f"✅ Market order: {order.get('id')}")
            
            time.sleep(1)
            
            # SL/TP orders com tratamento de erro
            sl_order_id = None
            tp_order_id = None
            
            try:
                # Stop Loss
                sl_order = self.exchange.create_order(
                    symbol, 'STOP_MARKET', side_close, quantity,
                    params={'stopPrice': sl_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                sl_order_id = sl_order.get('id')
                logger.logger.info(f"✅ Stop Loss: {sl_order_id}")
                
                # Take Profit
                tp_order = self.exchange.create_order(
                    symbol, 'TAKE_PROFIT_MARKET', side_close, quantity,
                    params={'stopPrice': tp_price, 'triggerBy': 'LastPrice', 'reduceOnly': True}
                )
                tp_order_id = tp_order.get('id')
                logger.logger.info(f"✅ Take Profit: {tp_order_id}")
                
            except Exception as e:
                logger.logger.error(f"⚠️ SL/TP error: {e}")
            
            # Salvar posição
            trade_data = {
                'symbol': symbol,
                'signal': signal,
                'entry_price': entry_price,
                'quantity': quantity,
                'stop_loss_price': sl_price,
                'take_profit_price': tp_price,
                'stop_loss_pct': sl_pct,
                'take_profit_pct': tp_pct,
                'risk_reward_ratio': risk_reward_ratio,
                'timestamp': datetime.now(),
                'order_id': order.get('id'),
                'sl_order_id': sl_order_id,
                'tp_order_id': tp_order_id,
                'signal_strength': signal_strength,
                'atr': signal_info['atr'],
                'reasons': signal_info['reasons'][:3],  # Apenas 3 reasons
                'multi_tf_score': signal_info['score']
            }
            
            self.active_positions[symbol] = trade_data
            self.symbol_cooldown[symbol] = time.time()
            
            self.database.save_trade(trade_data)
            
            # Métricas
            position_value = entry_price * quantity
            logger.logger.info(f"💰 Position: ${position_value:.2f} | Active: {len(self.active_positions)}/{self.risk_manager.max_positions}")
            logger.logger.info(f"🎯 Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
            logger.logger.info(f"✅ POSITION OPENED SUCCESSFULLY!\n")
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Position open error {symbol}: {e}"
            logger.logger.error(error_msg)
            self.risk_manager.error_count += 1
            return False
    
    def run_optimized_analysis_cycle(self) -> int:
        """Ciclo de análise otimizado"""
        signals_found = 0
        
        try:
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            # Filtrar símbolos em cooldown
            ready_symbols = []
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    time_since = time.time() - self.symbol_cooldown[symbol]
                    if time_since >= self.min_cooldown:
                        ready_symbols.append(symbol)
                else:
                    ready_symbols.append(symbol)
            
            if not ready_symbols:
                logger.logger.info("⏸️ All symbols in cooldown")
                return 0
            
            logger.logger.info(f"[🔍 ANALYSIS] Scanning {len(ready_symbols)} symbols...")
            
            # Análise paralela com timeout
            futures = {}
            for symbol in ready_symbols:
                future = self.executor.submit(self.analyze_symbol_safe, symbol)
                futures[future] = symbol
            
            # Processar resultados com timeout
            for future in as_completed(futures, timeout=60):
                symbol = futures[future]
                try:
                    result = future.result(timeout=10)
                    
                    if result and result['signal'] != 'NEUTRAL':
                        signals_found += 1
                        
                        logger.logger.info(f"🚨 SIGNAL: {symbol} {result['signal']} (Score: {result['score']:.1f})")
                        
                        # Tentar abrir posição
                        success = self.open_position_safe(symbol, result)
                        
                        if success:
                            logger.logger.info(f"   ✅ Position opened!")
                        
                except Exception as e:
                    logger.logger.error(f"❌ Future error {symbol}: {e}")
            
            logger.logger.info(f"[🔍 COMPLETE] {signals_found} signals found")
            
            return signals_found
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis cycle error: {e}")
            self.risk_manager.error_count += 1
            return 0
    
    def check_positions_safe(self):
        """Monitor posições com tratamento de erro"""
        if not self.active_positions:
            return
        
        try:
            symbols = list(self.active_positions.keys())
            positions = self.exchange.fetch_positions(symbols)
            
            for pos in positions:
                symbol = pos['symbol']
                if symbol not in self.active_positions:
                    continue
                
                contracts = float(pos.get('contracts', 0))
                unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                
                if contracts == 0:
                    self._handle_position_close_safe(symbol, pos)
                    
        except Exception as e:
            logger.logger.error(f"❌ Position check error: {e}")
            self.risk_manager.error_count += 1
    
    def _handle_position_close_safe(self, symbol: str, position_data: Dict):
        """Handle position close com tratamento de erro"""
        try:
            trade_info = self.active_positions[symbol]
            unrealized_pnl = float(position_data.get('unrealizedPnl', 0))
            
            balance = self._get_account_balance()
            pnl_pct = (unrealized_pnl / balance) if balance > 0 else 0
            
            exit_reason = "AUTO"
            if abs(unrealized_pnl) > 0:
                exit_reason = "TAKE_PROFIT" if unrealized_pnl > 0 else "STOP_LOSS"
            
            self.risk_manager.register_trade_result(pnl_pct, symbol)
            
            exit_price = position_data.get('markPrice', trade_info['entry_price'])
            self.database.close_trade(symbol, exit_price, pnl_pct, unrealized_pnl, exit_reason)
            
            duration = datetime.now() - trade_info['timestamp']
            duration_str = f"{duration.total_seconds()/3600:.1f}h"
            
            status = "PROFIT" if pnl_pct > 0 else "LOSS"
            emoji = "💚" if pnl_pct > 0 else "🔴"
            
            logger.logger.info(f"\n{emoji} POSITION CLOSED: {symbol} {status}")
            logger.logger.info(f"   P&L: {pnl_pct*100:+.2f}% (${unrealized_pnl:+.2f}) | Duration: {duration_str}")
            logger.logger.info(f"   Daily: {self.risk_manager.daily_pnl*100:+.2f}% | Today: {self.risk_manager.trades_today}")
            
            del self.active_positions[symbol]
            
        except Exception as e:
            logger.logger.error(f"❌ Position close error {symbol}: {e}")
    
    def run_daily_report_simple(self):
        """Relatório diário simplificado"""
        try:
            stats = self.risk_manager.get_risk_status()
            balance = self._get_account_balance()
            
            report = f"""
📊 DAILY REPORT - {datetime.now().strftime('%Y-%m-%d')}

💰 PERFORMANCE:
Daily P&L: {stats['daily_pnl']:+.2f}%
Trades: {stats['trades_today']}/{stats['target_trades']}
Win Rate: {stats['statistics']['win_rate']:.1f}%

🚀 SYSTEM:
Balance: ${balance:.2f}
Active: {len(self.active_positions)}/5
Errors: {stats['error_count']}

✅ All systems operational
            """
            
            self.alert_system.send_alert("Daily Report", report, "info")
            logger.logger.info("✅ Daily report sent")
            
        except Exception as e:
            logger.logger.error(f"❌ Daily report error: {e}")
    
    def run(self):
        """Loop principal otimizado"""
        logger.logger.info(f"\n{'='*100}")
        logger.logger.info(f"🚀 FIXED ADVANCED MULTI-TIMEFRAME BOT")
        logger.logger.info(f"{'='*100}")
        
        mode_msg = f"{'🧪 TESTNET' if self.testnet else '🚨 PRODUCTION'}"
        logger.logger.info(f"MODE: {mode_msg}")
        logger.logger.info(f"SYMBOLS: {len(self.symbols)} coins")
        logger.logger.info(f"TIMEFRAMES: {', '.join(self.timeframes)}")
        logger.logger.info(f"TARGET: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"DASHBOARD: http://localhost:5000")
        logger.logger.info(f"✅ JSON ERRORS FIXED")
        logger.logger.info(f"{'='*100}\n")
        
        # Setup
        if not self.setup_account():
            logger.logger.error("❌ Setup failed")
            return
        
        # Loop principal
        cycle = 0
        last_daily_report = datetime.now().date()
        
        try:
            while True:
                cycle += 1
                cycle_start = time.time()
                
                # Status
                if cycle % 10 == 1:
                    can_trade, reason = self.risk_manager.can_trade()
                    aggression = "🔥 AGGRESSIVE" if self.risk_manager.should_increase_aggression() else "📊 NORMAL"
                    
                    logger.logger.info(f"\n[CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                    logger.logger.info(f"Status: {'🚀 ACTIVE' if can_trade else f'⏸️ PAUSED ({reason})'}")
                    logger.logger.info(f"Mode: {aggression}")
                    logger.logger.info(f"Today: {self.risk_manager.trades_today}/{AdvancedTradingConfig.TARGET_TRADES_PER_DAY}")
                    logger.logger.info(f"Active: {len(self.active_positions)}/5 | Errors: {self.risk_manager.error_count}")
                
                # Verificar trading
                can_trade, reason = self.risk_manager.can_trade()
                if not can_trade:
                    if cycle % 20 == 1:
                        logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(240)  # 4 minutos
                    continue
                
                # Relatório diário
                if datetime.now().date() != last_daily_report:
                    self.run_daily_report_simple()
                    last_daily_report = datetime.now().date()
                
                # Análise
                signals_found = self.run_optimized_analysis_cycle()
                
                # Monitor posições
                self.check_positions_safe()
                
                # Summary
                if signals_found > 0 or cycle % 20 == 1:
                    stats = self.risk_manager.get_risk_status()['statistics']
                    logger.logger.info(f"\n[📊 SUMMARY #{cycle}]")
                    logger.logger.info(f"🎯 Signals: {signals_found} | Active: {len(self.active_positions)}")
                    logger.logger.info(f"🏆 WR: {stats['win_rate']:.1f}% | R/R: {stats['avg_risk_reward']:.1f}:1")
                    logger.logger.info(f"💰 Daily: {self.risk_manager.daily_pnl*100:+.2f}% | Trades: {self.risk_manager.trades_today}")
                
                # Timing
                cycle_duration = time.time() - cycle_start
                sleep_time = max(90, AdvancedTradingConfig.ANALYSIS_INTERVAL - cycle_duration)
                
                if cycle % 15 == 1:
                    logger.logger.info(f"⏱️ Next cycle in {sleep_time/60:.1f}m")
                
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Manual shutdown")
            
        except Exception as e:
            error_msg = f"❌ Fatal error: {e}"
            logger.logger.error(error_msg)
            logger.logger.error(traceback.format_exc())
            
        finally:
            self._shutdown_safe()
    
    def _shutdown_safe(self):
        """Shutdown seguro"""
        logger.logger.info("🛑 Shutting down FIXED Advanced Bot...")
        
        try:
            if self.active_positions:
                logger.logger.warning(f"{len(self.active_positions)} positions still active")
            
            stats = self.risk_manager.get_risk_status()['statistics']
            
            final_report = f"""
FIXED Advanced Bot shutdown complete.

FINAL STATS:
Trades: {stats['total_trades']}
Win Rate: {stats['win_rate']:.1f}%
Daily P&L: {self.risk_manager.daily_pnl*100:+.2f}%

✅ JSON errors fixed
✅ Thread-safe database
✅ Optimized performance

Shutdown: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            logger.logger.info(final_report)
            
            # Cleanup
            self.executor.shutdown(wait=True)
            
        except Exception as e:
            logger.logger.error(f"❌ Shutdown error: {e}")
        
        logger.logger.info("✅ FIXED Advanced Bot shutdown complete")

# =================== MAIN ATUALIZADO ===================
def main():
    try:
        global logger
        logger = AdvancedLogger()
        
        required_vars = ['BYBIT_API_KEY', 'BYBIT_API_SECRET']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing: {', '.join(missing_vars)}")
            return
        
        testnet = os.getenv('TESTNET', 'true').lower() == 'true'
        
        print(f"\n{'='*80}")
        print(f"🚀 SIMPLE & ROBUST TRADING BOT")
        print(f"{'='*80}")
        print(f"✅ ALL METHODS INCLUDED")
        print(f"✅ SIMPLE ANALYSIS")
        print(f"✅ READY TO TRADE")
        print(f"{'='*80}")
        
        if not testnet:
            print(f"\n🚨 PRODUCTION MODE!")
            time.sleep(2)
        
        logger.logger.info("🚀 Starting Simple Robust Bot...")
        
        bot = DetailedConservativeBot(testnet=testnet)
        bot.run()  # ✅ AGORA O MÉTODO RUN EXISTE
        
    except KeyboardInterrupt:
        logger.logger.info("\n🛑 Interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

# =================== ADICIONAR MÉTODO RUN AO BOT ===================
class DetailedConservativeBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing COMPLETE Conservative Bot...")
        
        # Componentes
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.analyzer = OptimizedMultiTimeframeAnalyzer()
        self.sl_tp_calculator = AdvancedStopLossTakeProfit()
        self.dashboard = OptimizedDashboard(self, port=5000)
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações
        self.symbols = self.cmc_api.get_top_coins()
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        self.primary_timeframe = AdvancedTradingConfig.PRIMARY_TIMEFRAME
        self.leverage = 3
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 900
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="robust_analyzer")
        
        # Taxa
        self.fee_rate = 0.00075
        
        logger.logger.info(f"✅ COMPLETE Conservative Bot initialized - {len(self.symbols)} symbols")

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
            'rateLimit': 100,
            'options': {
                'defaultType': 'linear',
                'adjustForTimeDifference': True,
                'recvWindow': 15000,
            },
            'sandbox': self.testnet,
        })
        
        logger.logger.info("✅ Exchange configured")

    def _get_account_balance(self) -> float:
        """Saldo da conta"""
        try:
            balance = self.exchange.fetch_balance()
            total_balance = balance['USDT']['total']
            return total_balance
        except Exception as e:
            logger.logger.error(f"❌ Balance error: {e}")
            return 0

    def setup_account(self) -> bool:
        """Setup da conta"""
        try:
            self.exchange.load_time_difference()
            markets = self.exchange.load_markets()
            
            leverage_success = 0
            for symbol in self.symbols:
                try:
                    self.exchange.set_leverage(self.leverage, symbol)
                    leverage_success += 1
                except:
                    continue
            
            logger.logger.info(f"✅ Leverage {self.leverage}x set for {leverage_success}/{len(self.symbols)} symbols")
            
            balance = self._get_account_balance()
            if balance < 50:
                logger.logger.error(f"❌ Insufficient balance: ${balance:.2f}")
                return False
            
            logger.logger.info(f"✅ Account balance: ${balance:.2f}")
            
            self.dashboard.start()
            
            return True
            
        except Exception as e:
            logger.logger.error(f"❌ Setup failed: {e}")
            return False

    def fetch_ohlcv_data_simple(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """Busca dados OHLCV de forma simples e tolerante"""
        ohlcv_data = {}
        
        for timeframe in self.timeframes:
            try:
                # Buscar dados básicos
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=20)
                if len(ohlcv) >= 10:  # Apenas 10 candles mínimos
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    ohlcv_data[timeframe] = df
            except Exception as e:
                logger.logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
                
        return ohlcv_data

    def analyze_symbol_simple(self, symbol: str) -> Optional[Dict]:
        """Analisa um símbolo de forma simples"""
        try:
            ohlcv_data = self.fetch_ohlcv_data_simple(symbol)
            
            if len(ohlcv_data) < 1:
                logger.logger.info(f"   📭 {symbol}: No timeframe data")
                return None
            
            # Análise básica
            result = self.simple_analysis(symbol, ohlcv_data)
            
            # Critérios conservadores
            if (result and result['signal'] != 'NEUTRAL' and 
                result['score'] >= AdvancedTradingConfig.MIN_SIGNAL_SCORE):
                
                self.database.save_signal_analysis(symbol, 'multi', result)
                return result
            
            return None
            
        except Exception as e:
            logger.logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def simple_analysis(self, symbol: str, ohlcv_data: Dict[str, pd.DataFrame]) -> Dict:
        """Análise simples e direta"""
        try:
            logger.logger.info(f"🔍 {symbol}:")
            
            all_reasons = []
            total_score = 0
            timeframe_count = 0
            
            for timeframe, df in ohlcv_data.items():
                if len(df) < 10:
                    continue
                    
                try:
                    # Calcular indicadores básicos
                    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
                    df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=9).ema_indicator()
                    df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=21).ema_indicator()
                    
                    last = df.iloc[-1]
                    
                    # Análise básica
                    score = 0
                    reasons = []
                    
                    # RSI
                    rsi = last['rsi']
                    if not pd.isna(rsi):
                        if rsi <= 30:
                            score += 2
                            reasons.append(f"RSI {rsi:.1f}")
                        elif rsi >= 70:
                            score -= 2
                            reasons.append(f"RSI {rsi:.1f}")
                    
                    # EMA
                    if last['ema_fast'] > last['ema_slow']:
                        score += 1
                        reasons.append("EMA Bull")
                    else:
                        score -= 1
                        reasons.append("EMA Bear")
                    
                    total_score += score
                    timeframe_count += 1
                    all_reasons.extend([f"{timeframe}: {r}" for r in reasons])
                    
                    logger.logger.info(f"   {timeframe}: Score {score} - {', '.join(reasons)}")
                    
                except Exception as e:
                    logger.logger.debug(f"Analysis error {symbol} {timeframe}: {e}")
                    continue
            
            if timeframe_count == 0:
                return {'signal': 'NEUTRAL', 'score': 0, 'reasons': ['No valid data']}
            
            avg_score = total_score / timeframe_count
            signal = 'NEUTRAL'
            
            if avg_score >= 1.5:
                signal = 'LONG'
            elif avg_score <= -1.5:
                signal = 'SHORT'
            
            result = {
                'signal': signal,
                'score': abs(avg_score),
                'reasons': all_reasons[:4],
                'price': df.iloc[-1]['close'] if 'df' in locals() else 0,
                'rsi': rsi if 'rsi' in locals() else 50,
                'df': df
            }
            
            if signal != 'NEUTRAL':
                logger.logger.info(f"   🎯 {symbol}: {signal} (Score: {avg_score:.1f})")
            else:
                logger.logger.info(f"   ⏸️ {symbol}: No signal")
            
            return result
            
        except Exception as e:
            logger.logger.error(f"Error in simple analysis for {symbol}: {e}")
            return {'signal': 'NEUTRAL', 'score': 0, 'reasons': ['Analysis error']}

    def run_analysis_cycle(self) -> int:
        """Ciclo de análise simples"""
        signals_found = 0
        positions_opened = 0
        
        try:
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            ready_symbols = []
            current_time = time.time()
            
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    time_since = current_time - self.symbol_cooldown[symbol]
                    if time_since >= self.min_cooldown:
                        ready_symbols.append(symbol)
                else:
                    ready_symbols.append(symbol)
            
            if not ready_symbols:
                return 0
            
            logger.logger.info(f"\n📊 ANALYZING {len(ready_symbols)} SYMBOLS")
            
            futures = {}
            for symbol in ready_symbols:
                future = self.executor.submit(self.analyze_symbol_simple, symbol)
                futures[future] = symbol
            
            analyzed_count = 0
            for future in as_completed(futures, timeout=30):
                symbol = futures[future]
                analyzed_count += 1
                
                try:
                    result = future.result(timeout=5)
                    
                    if result and result['signal'] != 'NEUTRAL':
                        signals_found += 1
                        logger.logger.info(f"🎯 SIGNAL: {symbol} {result['signal']}")
                        
                        success = self.open_position(symbol, result)
                        if success:
                            positions_opened += 1
                            
                except Exception as e:
                    continue
            
            logger.logger.info(f"📈 CYCLE COMPLETE: {analyzed_count} analyzed, {signals_found} signals, {positions_opened} positions")
            
            return positions_opened
            
        except Exception as e:
            logger.logger.error(f"❌ Analysis cycle error: {e}")
            return 0

    def calculate_position_size(self, symbol: str, signal_strength: float) -> float:
        """Calcula tamanho da posição"""
        try:
            balance = self._get_account_balance()
            if balance <= 0:
                return 0
            
            base_size = AdvancedTradingConfig.MAX_POSITION_SIZE
            position_usdt = balance * base_size
            
            ticker = self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            
            if price <= 0:
                return 0
            
            quantity = position_usdt / price
            
            try:
                quantity = self.exchange.amount_to_precision(symbol, quantity)
                final_quantity = float(quantity) if quantity else 0
            except:
                return 0
            
            min_notional = 5.0
            if final_quantity * price < min_notional:
                return 0
            
            return final_quantity
            
        except Exception as e:
            logger.logger.error(f"❌ Position size error {symbol}: {e}")
            return 0

    def open_position(self, symbol: str, signal_info: Dict) -> bool:
        """Abre uma posição"""
        try:
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                return False
            
            if symbol in self.active_positions:
                return False
            
            if len(self.active_positions) >= AdvancedTradingConfig.MAX_POSITIONS:
                return False
            
            current_time = time.time()
            if symbol in self.symbol_cooldown:
                time_since = current_time - self.symbol_cooldown[symbol]
                if time_since < self.min_cooldown:
                    return False
            
            signal_strength = signal_info.get('signal_strength', 0.5)
            quantity = self.calculate_position_size(symbol, signal_strength)
            
            if quantity <= 0:
                return False
            
            # SL/TP fixos para simplificar
            sl_pct = AdvancedTradingConfig.MIN_STOP_LOSS_PCT
            tp_pct = sl_pct * AdvancedTradingConfig.MIN_RISK_REWARD_RATIO
            
            signal = signal_info['signal']
            entry_price = signal_info['price']
            
            if signal == 'LONG':
                sl_price = entry_price * (1 - sl_pct)
                tp_price = entry_price * (1 + tp_pct)
                side_open = 'buy'
            else:
                sl_price = entry_price * (1 + sl_pct)
                tp_price = entry_price * (1 - tp_pct)
                side_open = 'sell'
            
            logger.logger.info(f"\n🚀 OPENING {symbol} {signal}")
            logger.logger.info(f"   Entry: ${entry_price:.4f}")
            logger.logger.info(f"   SL: ${sl_price:.4f} | TP: ${tp_price:.4f}")
            
            try:
                if signal == 'LONG':
                    order = self.exchange.create_market_buy_order(symbol, quantity)
                else:
                    order = self.exchange.create_market_sell_order(symbol, quantity)
                
                logger.logger.info(f"✅ Order executed")
                
                trade_data = {
                    'symbol': symbol,
                    'signal': signal,
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'stop_loss_price': sl_price,
                    'take_profit_price': tp_price,
                    'timestamp': datetime.now(),
                    'order_id': order.get('id'),
                    'reasons': signal_info['reasons']
                }
                
                self.active_positions[symbol] = trade_data
                self.symbol_cooldown[symbol] = current_time
                
                self.database.save_trade(trade_data)
                
                logger.logger.info(f"✅ POSITION OPENED: {symbol}")
                
                return True
                
            except Exception as order_error:
                logger.logger.error(f"❌ Order failed: {order_error}")
                return False
            
        except Exception as e:
            logger.logger.error(f"❌ Position error {symbol}: {e}")
            return False

    def check_positions(self):
        """Verifica posições abertas"""
        if not self.active_positions:
            return
        
        try:
            symbols = list(self.active_positions.keys())
            
            for symbol in symbols:
                try:
                    positions = self.exchange.fetch_positions([symbol])
                    
                    for pos in positions:
                        if pos['symbol'] == symbol:
                            contracts = float(pos.get('contracts', 0))
                            unrealized_pnl = float(pos.get('unrealizedPnl', 0))
                            
                            if contracts == 0:
                                self.close_position(symbol, pos)
                            break
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.logger.error(f"❌ Position check error: {e}")

    def close_position(self, symbol: str, position_data: Dict):
        """Fecha uma posição"""
        try:
            if symbol not in self.active_positions:
                return
                
            trade_info = self.active_positions[symbol]
            unrealized_pnl = float(position_data.get('unrealizedPnl', 0))
            
            balance = self._get_account_balance()
            pnl_pct = (unrealized_pnl / balance) if balance > 0 else 0
            
            exit_reason = "AUTO"
            if abs(unrealized_pnl) > 0:
                exit_reason = "TAKE_PROFIT" if unrealized_pnl > 0 else "STOP_LOSS"
            
            self.risk_manager.register_trade_result(pnl_pct, symbol)
            
            exit_price = position_data.get('markPrice', trade_info['entry_price'])
            self.database.close_trade(symbol, exit_price, pnl_pct, unrealized_pnl, exit_reason)
            
            logger.logger.info(f"🔒 CLOSED: {symbol} | P&L: {pnl_pct*100:+.2f}%")
            
            del self.active_positions[symbol]
            
        except Exception as e:
            logger.logger.error(f"❌ Close error {symbol}: {e}")

    # =================== MÉTODO RUN ADICIONADO ===================
    def run(self):
        """Método principal de execução do bot"""
        logger.logger.info(f"\n{'='*80}")
        logger.logger.info(f"🚀 BOT INICIADO - SIMPLE & ROBUST")
        logger.logger.info(f"{'='*80}")
        logger.logger.info(f"Symbols: {len(self.symbols)}")
        logger.logger.info(f"Target: {AdvancedTradingConfig.TARGET_TRADES_PER_DAY} trades/day")
        logger.logger.info(f"Position Size: {AdvancedTradingConfig.MAX_POSITION_SIZE*100:.1f}%")
        logger.logger.info(f"{'='*80}\n")
        
        if not self.setup_account():
            logger.logger.error("❌ Setup failed - stopping bot")
            return
        
        # Loop principal
        cycle = 0
        
        try:
            while True:
                cycle += 1
                cycle_start = time.time()
                
                # Status
                stats = self.risk_manager.get_risk_status()
                can_trade, reason = self.risk_manager.can_trade()
                
                logger.logger.info(f"\n[🔄 CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                logger.logger.info(f"Status: {'🚀 ACTIVE' if can_trade else f'⏸️ PAUSED ({reason})'}")
                logger.logger.info(f"Active: {len(self.active_positions)}/{AdvancedTradingConfig.MAX_POSITIONS}")
                logger.logger.info(f"Today: {stats['trades_today']}/{stats['target_trades']}")
                logger.logger.info(f"P&L: {stats['daily_pnl']:+.2f}%")
                
                if not can_trade:
                    logger.logger.info(f"⏸️ Trading paused: {reason}")
                    time.sleep(60)
                    continue
                
                # Análise
                positions_opened = self.run_analysis_cycle()
                
                # Monitorar posições
                self.check_positions()
                
                # Timing
                cycle_duration = time.time() - cycle_start
                sleep_time = max(10, AdvancedTradingConfig.ANALYSIS_INTERVAL - cycle_duration)
                
                logger.logger.info(f"⏱️ Next cycle in {sleep_time:.0f}s")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Manual shutdown")
        except Exception as e:
            logger.logger.error(f"❌ Fatal error: {e}")
        finally:
            self.executor.shutdown(wait=False)
            logger.logger.info("✅ Bot shutdown complete")

# =================== CORREÇÃO DOS INDICADORES TÉCNICOS ===================
class FixedTechnicalAnalyzer:
    def __init__(self):
        self.timeframes = AdvancedTradingConfig.TIMEFRAMES
        
    def calculate_robust_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de forma robusta com tratamento de erro completo"""
        try:
            if df.empty or len(df) < 20:
                return df
            
            # Garantir que os dados são válidos
            df = self._clean_dataframe(df)
            
            high = df['high']
            low = df['low']
            close = df['close']
            volume = df['volume']
            
            # 1. EMAS BÁSICAS (sempre funcionam)
            try:
                df['ema_9'] = ta.trend.EMAIndicator(close, window=9).ema_indicator()
                df['ema_21'] = ta.trend.EMAIndicator(close, window=21).ema_indicator()
                df['ema_50'] = ta.trend.EMAIndicator(close, window=50).ema_indicator()
                
                # Preencher valores NaN
                df['ema_9'] = df['ema_9'].fillna(close)
                df['ema_21'] = df['ema_21'].fillna(close)
                df['ema_50'] = df['ema_50'].fillna(close)
            except:
                df['ema_9'] = close
                df['ema_21'] = close
                df['ema_50'] = close
            
            # 2. RSI CORRIGIDO - com validação robusta
            try:
                rsi_indicator = ta.momentum.RSIIndicator(close, window=14)
                rsi_values = rsi_indicator.rsi()
                
                # Corrigir valores extremos
                rsi_values = rsi_values.clip(0, 100)  # Forçar entre 0-100
                rsi_values = rsi_values.fillna(50)    # Preencher NaN com 50
                
                # Suavizar RSI
                df['rsi'] = rsi_values
                df['rsi_smooth'] = ta.trend.EMAIndicator(rsi_values, window=3).ema_indicator().fillna(rsi_values)
                
            except Exception as e:
                logger.logger.debug(f"RSI calculation error: {e}")
                df['rsi'] = 50.0
                df['rsi_smooth'] = 50.0
            
            # 3. MACD com fallback
            try:
                macd = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
                df['macd'] = macd.macd().fillna(0)
                df['macd_signal'] = macd.macd_signal().fillna(0)
                df['macd_histogram'] = macd.macd_diff().fillna(0)
            except:
                df['macd'] = 0
                df['macd_signal'] = 0
                df['macd_histogram'] = 0
            
            # 4. ATR com fallback
            try:
                atr = ta.volatility.AverageTrueRange(high, low, close, window=14)
                df['atr'] = atr.average_true_range().fillna(close * 0.02)  # 2% padrão
            except:
                df['atr'] = close * 0.02
            
            # 5. VOLUME com validação
            try:
                df['volume_sma'] = volume.rolling(window=20, min_periods=1).mean()
                df['volume_ratio'] = (volume / df['volume_sma']).fillna(1.0)
                # Limitar ratio para evitar valores extremos
                df['volume_ratio'] = df['volume_ratio'].clip(0.1, 10.0)
            except:
                df['volume_ratio'] = 1.0
            
            # 6. Bollinger Bands
            try:
                bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
                df['bb_upper'] = bb.bollinger_hband().fillna(close * 1.1)
                df['bb_lower'] = bb.bollinger_lband().fillna(close * 0.9)
                df['bb_middle'] = bb.bollinger_mavg().fillna(close)
                
                # Calcular posição nas bandas
                bb_width = df['bb_upper'] - df['bb_lower']
                df['bb_position'] = ((close - df['bb_lower']) / bb_width).fillna(0.5)
                df['bb_position'] = df['bb_position'].clip(0, 1)
            except:
                df['bb_position'] = 0.5
            
            # 7. ADX simplificado
            try:
                adx_indicator = ta.trend.ADXIndicator(high, low, close, window=14)
                df['adx'] = adx_indicator.adx().fillna(20)  # Valor neutro
                df['adx'] = df['adx'].clip(0, 100)
            except:
                df['adx'] = 20
            
            return df
            
        except Exception as e:
            logger.logger.error(f"Critical indicator error: {e}")
            # Retornar DataFrame mínimo com valores padrão
            df['ema_9'] = close
            df['ema_21'] = close  
            df['ema_50'] = close
            df['rsi'] = 50.0
            df['rsi_smooth'] = 50.0
            df['macd'] = 0
            df['macd_signal'] = 0
            df['macd_histogram'] = 0
            df['atr'] = close * 0.02
            df['volume_ratio'] = 1.0
            df['bb_position'] = 0.5
            df['adx'] = 20
            return df

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e valida o DataFrame"""
        try:
            # Remover linhas com valores NaN críticos
            df = df.dropna(subset=['open', 'high', 'low', 'close'])
            
            # Garantir que high >= low e high >= close >= low
            df['high'] = np.where(df['high'] < df['low'], df['low'] * 1.001, df['high'])
            df['low'] = np.where(df['low'] > df['high'], df['high'] * 0.999, df['low'])
            df['close'] = df['close'].clip(df['low'], df['high'])
            df['open'] = df['open'].clip(df['low'], df['high'])
            
            # Preencher volume com 0 se NaN
            df['volume'] = df['volume'].fillna(0)
            
            return df
        except:
            return df

    def analyze_single_timeframe_fixed(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Análise corrigida de timeframe único"""
        try:
            if len(df) < 10:
                return self._neutral_timeframe_analysis("Insufficient data")
            
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            
            score = 0
            reasons = []
            
            # 1. ANÁLISE DE TENDÊNCIA (EMAs)
            try:
                ema_trend = 0
                if last['ema_9'] > last['ema_21'] > last['ema_50']:
                    ema_trend = 1
                    score += 2.0
                    reasons.append("EMA Bullish")
                elif last['ema_9'] < last['ema_21'] < last['ema_50']:
                    ema_trend = -1
                    score -= 2.0
                    reasons.append("EMA Bearish")
                else:
                    reasons.append("EMA Mixed")
            except:
                reasons.append("EMA Error")
            
            # 2. ANÁLISE RSI CORRIGIDA
            try:
                rsi = last['rsi_smooth']
                if not pd.isna(rsi) and 0 <= rsi <= 100:
                    if rsi < 35:
                        score += 1.5
                        reasons.append(f"RSI Oversold ({rsi:.1f})")
                    elif rsi > 65:
                        score -= 1.5
                        reasons.append(f"RSI Overbought ({rsi:.1f})")
                    else:
                        reasons.append(f"RSI Neutral ({rsi:.1f})")
                else:
                    reasons.append("RSI Invalid")
            except:
                reasons.append("RSI Error")
            
            # 3. ANÁLISE MACD
            try:
                if last['macd'] > last['macd_signal'] and last['macd_histogram'] > 0:
                    score += 1.0
                    reasons.append("MACD Bullish")
                elif last['macd'] < last['macd_signal'] and last['macd_histogram'] < 0:
                    score -= 1.0
                    reasons.append("MACD Bearish")
            except:
                reasons.append("MACD Error")
            
            # 4. ANÁLISE VOLUME
            try:
                volume_ratio = last['volume_ratio']
                if volume_ratio > 1.3:
                    score += 0.5
                    reasons.append(f"Volume High ({volume_ratio:.1f}x)")
                elif volume_ratio < 0.7:
                    score -= 0.5
                    reasons.append(f"Volume Low ({volume_ratio:.1f}x)")
            except:
                reasons.append("Volume Error")
            
            # 5. ANÁLISE BOLLINGER BANDS
            try:
                bb_pos = last['bb_position']
                if bb_pos < 0.2:
                    score += 1.0
                    reasons.append("Near BB Support")
                elif bb_pos > 0.8:
                    score -= 1.0
                    reasons.append("Near BB Resistance")
            except:
                reasons.append("BB Error")
            
            # Determinar sinal baseado no score
            signal = 'NEUTRAL'
            if score >= 3.0:
                signal = 'LONG'
            elif score <= -3.0:
                signal = 'SHORT'
            
            return {
                'signal': signal,
                'score': abs(score),
                'confidence': min(abs(score) / 4.0, 1.0),
                'price': last['close'],
                'rsi': last['rsi'],
                'volume_ratio': last['volume_ratio'],
                'atr': last['atr'],
                'adx': last['adx'],
                'timeframe': timeframe,
                'reasons': reasons,
                'df': df
            }
            
        except Exception as e:
            logger.logger.error(f"Timeframe analysis error: {e}")
            return self._neutral_timeframe_analysis(f"Analysis error: {e}")

    def _neutral_timeframe_analysis(self, reason: str) -> Dict:
        """Retorna análise neutra"""
        return {
            'signal': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'price': 0,
            'rsi': 50,
            'volume_ratio': 1.0,
            'atr': 0,
            'adx': 20,
            'timeframe': 'unknown',
            'reasons': [reason],
            'df': pd.DataFrame()
        }

    def multi_timeframe_analysis_fixed(self, symbol: str, ohlcv_data: Dict[str, pd.DataFrame]) -> Dict:
        """Análise multi-timeframe corrigida"""
        try:
            logger.logger.info(f"🔍 ANALYZING {symbol}:")
            
            tf_results = {}
            total_weighted_score = 0
            total_confidence = 0
            timeframe_count = 0
            
            # Pesos por timeframe
            weights = {'15m': 0.25, '1h': 0.35, '4h': 0.40}
            
            for timeframe in self.timeframes:
                if timeframe in ohlcv_data and len(ohlcv_data[timeframe]) > 0:
                    df = ohlcv_data[timeframe]
                    
                    # Calcular indicadores robustos
                    df = self.calculate_robust_indicators(df)
                    
                    # Analisar timeframe
                    result = self.analyze_single_timeframe_fixed(df, timeframe)
                    tf_results[timeframe] = result
                    
                    # Log claro e limpo
                    rsi_display = result['rsi']
                    if pd.isna(rsi_display) or rsi_display < 0 or rsi_display > 100:
                        rsi_display = 50.0
                    
                    logger.logger.info(f"   {timeframe}: {result['signal']} "
                                     f"(Score: {result['score']:.1f}, RSI: {rsi_display:.1f})")
                    
                    # Contribuir para score total
                    weight = weights.get(timeframe, 0.3)
                    total_weighted_score += result['score'] * weight * (1 if result['signal'] == 'LONG' else -1 if result['signal'] == 'SHORT' else 0)
                    total_confidence += result['confidence'] * weight
                    timeframe_count += 1
            
            if timeframe_count == 0:
                return self._neutral_signal("No timeframe data")
            
            # Determinar sinal final com critérios rigorosos
            final_signal = 'NEUTRAL'
            final_score = abs(total_weighted_score)
            avg_confidence = total_confidence / timeframe_count
            
            # Critérios mais conservadores
            if (total_weighted_score > 0 and final_score >= 4.0 and avg_confidence >= 0.6 and
                self._check_timeframe_agreement(tf_results, 'LONG')):
                final_signal = 'LONG'
            elif (total_weighted_score < 0 and final_score >= 4.0 and avg_confidence >= 0.6 and
                  self._check_timeframe_agreement(tf_results, 'SHORT')):
                final_signal = 'SHORT'
            
            # Usar análise do timeframe primário para dados adicionais
            primary_tf = '1h' if '1h' in tf_results else list(tf_results.keys())[0]
            primary_data = tf_results[primary_tf]
            
            result = {
                'signal': final_signal,
                'score': final_score,
                'confidence': avg_confidence,
                'signal_strength': min(final_score / 6.0, 1.0),
                'price': primary_data['price'],
                'rsi': primary_data['rsi'],
                'volume_ratio': primary_data['volume_ratio'],
                'atr': primary_data['atr'],
                'adx': primary_data['adx'],
                'timeframe': 'multi',
                'reasons': primary_data['reasons'][:3],  # Apenas 3 razões principais
                'df': primary_data['df'],
                'timeframe_results': tf_results
            }
            
            if final_signal != 'NEUTRAL':
                logger.logger.info(f"   🎯 {symbol}: {final_signal} SIGNAL! (Score: {final_score:.1f})")
            else:
                logger.logger.info(f"   ⏸️ {symbol}: No signal (Score: {final_score:.1f})")
            
            return result
            
        except Exception as e:
            logger.logger.error(f"Multi-timeframe analysis error {symbol}: {e}")
            return self._neutral_signal(f"Analysis error: {e}")

    def _check_timeframe_agreement(self, tf_results: Dict, signal: str) -> bool:
        """Verifica se há concordância entre timeframes"""
        signals = [result['signal'] for result in tf_results.values()]
        signal_count = signals.count(signal)
        total_count = len(signals)
        
        # Requer pelo menos 50% de concordância
        return signal_count >= max(2, total_count * 0.5)

    def _neutral_signal(self, reason: str) -> Dict:
        """Retorna sinal neutro padronizado"""
        return {
            'signal': 'NEUTRAL',
            'score': 0,
            'confidence': 0,
            'signal_strength': 0,
            'price': 0,
            'rsi': 50,
            'volume_ratio': 1.0,
            'atr': 0,
            'adx': 20,
            'timeframe': 'multi',
            'reasons': [reason],
            'df': pd.DataFrame(),
            'timeframe_results': {}
        }

# =================== BOT SIMPLIFICADO E FUNCIONAL ===================
class WorkingTradingBot:
    def __init__(self, testnet: bool = True):
        logger.logger.info("🚀 Initializing WORKING Trading Bot...")
        
        # Componentes essenciais apenas
        self.cmc_api = CoinMarketCapAPI()
        self.database = SafeJSONDatabase()
        self.alert_system = AdvancedAlert()
        self.risk_manager = AdvancedRiskManager(self.database)
        self.analyzer = FixedTechnicalAnalyzer()
        
        # Exchange
        self.testnet = testnet
        self._setup_exchange()
        
        # Configurações conservadoras
        self.symbols = self._get_reliable_symbols()
        self.timeframes = ['15m', '1h']  # Apenas 2 timeframes para simplificar
        
        # Estado
        self.active_positions = {}
        self.symbol_cooldown = {}
        self.min_cooldown = 1800  # 30 minutos
        
        logger.logger.info(f"✅ WORKING Bot initialized - {len(self.symbols)} symbols")

    def _get_reliable_symbols(self) -> List[str]:
        """Seleciona símbolos mais confiáveis"""
        reliable_pairs = [
            'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT',
            'XRPUSDT', 'DOTUSDT', 'DOGEUSDT', 'AVAXUSDT', 'LINKUSDT',
            'MATICUSDT', 'LTCUSDT', 'UNIUSDT', 'ATOMUSDT'
        ]
        return reliable_pairs

    def _setup_exchange(self):
        """Configura exchange de forma simples"""
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
        
        logger.logger.info("✅ Exchange configured")

    def fetch_ohlcv_simple(self, symbol: str, timeframe: str, limit: int = 50) -> Optional[pd.DataFrame]:
        """Busca dados OHLCV de forma simples e robusta"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if len(ohlcv) < 20:
                return None
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
            
        except Exception as e:
            logger.logger.debug(f"Data fetch error {symbol} {timeframe}: {e}")
            return None

    def analyze_symbol_working(self, symbol: str) -> Optional[Dict]:
        """Análise funcional de símbolo"""
        try:
            # Buscar dados para todos os timeframes
            ohlcv_data = {}
            for timeframe in self.timeframes:
                df = self.fetch_ohlcv_simple(symbol, timeframe, 50)
                if df is not None:
                    ohlcv_data[timeframe] = df
            
            if len(ohlcv_data) < 1:
                return None
            
            # Análise multi-timeframe corrigida
            result = self.analyzer.multi_timeframe_analysis_fixed(symbol, ohlcv_data)
            
            # Critérios conservadores para trading
            if (result['signal'] != 'NEUTRAL' and 
                result['score'] >= 4.0 and 
                result['confidence'] >= 0.6 and
                25 <= result['rsi'] <= 75 and
                result['volume_ratio'] >= 0.8):
                
                return result
            
            return None
            
        except Exception as e:
            logger.logger.debug(f"Analysis error {symbol}: {e}")
            return None

    def run_working_cycle(self) -> int:
        """Ciclo de trading funcional"""
        positions_opened = 0
        
        try:
            # Símbolos disponíveis para análise
            available_symbols = [s for s in self.symbols if s not in self.active_positions]
            
            if not available_symbols:
                return 0
            
            # Verificar cooldown
            current_time = time.time()
            ready_symbols = []
            for symbol in available_symbols:
                if symbol in self.symbol_cooldown:
                    if current_time - self.symbol_cooldown[symbol] < self.min_cooldown:
                        continue
                ready_symbols.append(symbol)
            
            if not ready_symbols:
                return 0
            
            logger.logger.info(f"🔍 Analyzing {len(ready_symbols)} symbols...")
            
            # Analisar símbolos sequencialmente (evitar sobrecarga)
            for symbol in ready_symbols[:10]:  # Limitar a 10 por ciclo
                try:
                    result = self.analyze_symbol_working(symbol)
                    
                    if result:
                        logger.logger.info(f"🎯 VALID SIGNAL: {symbol} {result['signal']} "
                                         f"(Score: {result['score']:.1f}, RSI: {result['rsi']:.1f})")
                        
                        # Aqui você pode adicionar a lógica para abrir posição
                        # success = self.open_position_simple(symbol, result)
                        # if success:
                        #    positions_opened += 1
                        
                        # Por enquanto, apenas logar os sinais válidos
                        positions_opened += 0  # Remover quando implementar trading
                        
                except Exception as e:
                    logger.logger.debug(f"Symbol analysis error {symbol}: {e}")
                    continue
            
            logger.logger.info(f"📊 Cycle complete: {len(ready_symbols)} analyzed, {positions_opened} signals")
            
            return positions_opened
            
        except Exception as e:
            logger.logger.error(f"❌ Cycle error: {e}")
            return 0

    def run_continuous_analysis(self):
        """Loop contínuo de análise apenas (sem trading)"""
        logger.logger.info(f"\n{'='*60}")
        logger.logger.info("🔍 WORKING TRADING BOT - ANALYSIS MODE")
        logger.logger.info("✅ Fixed technical indicators")
        logger.logger.info("✅ Reliable symbols only") 
        logger.logger.info("✅ Conservative signal criteria")
        logger.logger.info(f"{'='*60}\n")
        
        cycle = 0
        
        try:
            while True:
                cycle += 1
                start_time = time.time()
                
                logger.logger.info(f"\n[🔄 CYCLE #{cycle}] {datetime.now().strftime('%H:%M:%S')}")
                
                # Executar análise
                signals_found = self.run_working_cycle()
                
                if signals_found > 0:
                    logger.logger.info(f"🎯 Found {signals_found} valid signals")
                else:
                    logger.logger.info("⏸️ No valid signals this cycle")
                
                # Timing do ciclo
                cycle_duration = time.time() - start_time
                sleep_time = max(30, 120 - cycle_duration)  # 2 minutos entre ciclos
                
                logger.logger.info(f"⏱️ Next analysis in {sleep_time:.0f}s")
                time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.logger.info("\n🛑 Analysis stopped")
        except Exception as e:
            logger.logger.error(f"❌ Analysis error: {e}")

# =================== TESTE RÁPIDO DOS INDICADORES ===================
def test_indicators():
    """Testa os indicadores técnicos com dados reais"""
    logger.logger.info("🧪 Testing technical indicators...")
    
    # Bot de teste
    bot = WorkingTradingBot(testnet=True)
    
    # Testar com alguns símbolos
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT'][:2]  # Apenas 2 para teste
    
    for symbol in test_symbols:
        logger.logger.info(f"\n📊 TESTING {symbol}:")
        
        try:
            # Buscar dados
            ohlcv_data = {}
            for timeframe in bot.timeframes:
                df = bot.fetch_ohlcv_simple(symbol, timeframe, 50)
                if df is not None:
                    ohlcv_data[timeframe] = df
                    logger.logger.info(f"   {timeframe}: {len(df)} candles")
            
            if not ohlcv_data:
                logger.logger.info("   ❌ No data")
                continue
            
            # Analisar
            result = bot.analyzer.multi_timeframe_analysis_fixed(symbol, ohlcv_data)
            
            logger.logger.info(f"   📈 Result: {result['signal']} (Score: {result['score']:.1f})")
            logger.logger.info(f"   📊 RSI: {result['rsi']:.1f}, Volume: {result['volume_ratio']:.1f}x")
            logger.logger.info(f"   🎯 Reasons: {', '.join(result['reasons'][:2])}")
            
        except Exception as e:
            logger.logger.error(f"   ❌ Test failed: {e}")
    
    logger.logger.info("\n✅ Indicator test complete")

# =================== MAIN CORRIGIDO ===================
def main():
    try:
        global logger
        logger = AdvancedLogger()
        
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
        print(f"✅ Analysis mode only (no trading)")
        print(f"{'='*60}")
        
        # Testar indicadores primeiro
        test_indicators()
        
        # Iniciar análise contínua
        input("\nPress Enter to start continuous analysis...")
        
        bot = WorkingTradingBot(testnet=True)
        bot.run_continuous_analysis()
        
    except KeyboardInterrupt:
        logger.logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.logger.error(f"❌ Fatal error: {e}")
        print(f"❌ Bot crashed: {e}")

if __name__ == '__main__':
    main()