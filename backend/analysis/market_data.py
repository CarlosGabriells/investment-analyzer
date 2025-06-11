"""
Módulo aprimorado para integração com APIs de dados de mercado
Foco principal em yfinance para dados de FIIs brasileiros com fallback para brapi.dev
"""

import logging
import requests
import yfinance as yf
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Importar configurações
from backend.config import settings

logger = logging.getLogger(__name__)

class EnhancedMarketDataProvider:
    """Provedor aprimorado de dados de mercado para FIIs brasileiros usando yfinance como principal fonte"""
    
    def __init__(self):
        self.brapi_base_url = "https://brapi.dev/api"
        self.brapi_api_key = settings.BRAPI_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Investment-Analyzer/1.0'
        })
        
        # Cache para dados de FIIs
        self._fii_cache = {}
        self._cache_ttl = 300  # 5 minutos
        
        logger.info("🚀 Enhanced Market Data Provider inicializado com yfinance como fonte principal")
    
    def _is_cache_valid(self, ticker: str) -> bool:
        """Verifica se o cache para um ticker ainda é válido"""
        if ticker not in self._fii_cache:
            return False
        
        cache_time = self._fii_cache[ticker].get('timestamp', 0)
        return (datetime.now().timestamp() - cache_time) < self._cache_ttl
    
    async def get_fii_data(self, ticker: str) -> Dict[str, Any]:
        """Busca dados completos do FII via yfinance primeiro, depois brapi.dev como fallback"""
        if not ticker or ticker == "N/A":
            return {"error": "Ticker inválido"}
        
        # Garantir formato correto do ticker
        ticker = ticker.upper()
        if not ticker.endswith('11'):
            ticker += '11'
        
        # Verificar cache primeiro
        if self._is_cache_valid(ticker):
            logger.info(f"📦 Usando dados do cache para {ticker}")
            return self._fii_cache[ticker]['data']
        
        try:
            # MÉTODO PRINCIPAL: yfinance
            logger.info(f"🎯 Buscando dados de {ticker} via yfinance...")
            ticker_yf = f"{ticker}.SA"
            
            # Criar objeto ticker do yfinance
            fii = yf.Ticker(ticker_yf)
            
            # Buscar informações básicas
            info = fii.info
            if not info or len(info) == 0:
                logger.warning(f"⚠️ yfinance não retornou dados para {ticker}, tentando brapi.dev...")
                return await self._get_brapi_fallback(ticker)
            
            # Buscar dados históricos
            historical_data = await self._get_yfinance_historical_data(fii, ticker)
            
            # Calcular métricas avançadas
            metrics = self._calculate_enhanced_metrics(info, historical_data)
            
            # Buscar dados de dividendos
            dividends_data = await self._get_yfinance_dividends(fii, ticker)
            
            # Compilar resultado
            result = {
                "ticker": ticker,
                "current_price": info.get('regularMarketPrice', info.get('currentPrice', 0)),
                "change_percent": info.get('regularMarketChangePercent', 0),
                "volume": info.get('regularMarketVolume', info.get('volume', 0)),
                "market_cap": info.get('marketCap', 0),
                "dividend_yield": self._extract_dividend_yield(info, dividends_data),
                "p_vp": info.get('priceToBook', self._calculate_price_to_book(info)),
                "fifty_two_week_high": info.get('fiftyTwoWeekHigh', 0),
                "fifty_two_week_low": info.get('fiftyTwoWeekLow', 0),
                "average_volume": info.get('averageDailyVolume10Day', info.get('averageVolume', 0)),
                "metrics": metrics,
                "historical_performance": historical_data,
                "dividends_analysis": dividends_data,
                "last_updated": datetime.now().isoformat(),
                "source": "yfinance_enhanced",
                "data_quality": "high"
            }
            
            # Armazenar no cache
            self._fii_cache[ticker] = {
                'data': result,
                'timestamp': datetime.now().timestamp()
            }
            
            logger.info(f"✅ Dados de {ticker} obtidos com sucesso via yfinance")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados via yfinance para {ticker}: {e}")
            # Fallback para brapi.dev
            logger.info(f"🔄 Tentando fallback brapi.dev para {ticker}...")
            return await self._get_brapi_fallback(ticker)
    
    def _extract_dividend_yield(self, info: Dict, dividends_data: Dict) -> float:
        """Extrai dividend yield com múltiplas tentativas"""
        # Tentar extrair do info primeiro
        dy_fields = ['dividendYield', 'trailingAnnualDividendYield', 'forwardDividendYield']
        for field in dy_fields:
            if field in info and info[field] is not None and info[field] > 0:
                return round(info[field] * 100, 2)  # Converter para percentual
        
        # Tentar calcular a partir dos dividendos
        if dividends_data and 'annual_yield' in dividends_data:
            return dividends_data['annual_yield']
        
        return 0.0
    
    def _calculate_price_to_book(self, info: Dict) -> float:
        """Calcula P/VP com diferentes métodos"""
        # Tentar campos diretos
        if 'priceToBook' in info and info['priceToBook'] is not None:
            return round(info['priceToBook'], 3)
        
        # Tentar calcular manualmente
        current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
        book_value = info.get('bookValue', 0)
        
        if current_price > 0 and book_value > 0:
            return round(current_price / book_value, 3)
        
        return 0.0
    
    async def _get_yfinance_historical_data(self, fii, ticker: str) -> Dict[str, Any]:
        """Busca dados históricos aprimorados do yfinance"""
        try:
            # Dados dos últimos 12 meses
            hist_1y = fii.history(period="1y")
            hist_3m = fii.history(period="3mo")
            hist_1m = fii.history(period="1mo")
            
            if hist_1y.empty:
                return {"error": "Dados históricos não disponíveis"}
            
            # Calcular retornos em diferentes períodos
            returns = {
                "returns_1d": self._calculate_return_period(hist_1y, 1),
                "returns_1w": self._calculate_return_period(hist_1y, 7),
                "returns_1m": self._calculate_return_period(hist_1y, 30),
                "returns_3m": self._calculate_return_period(hist_1y, 90),
                "returns_6m": self._calculate_return_period(hist_1y, 180),
                "returns_1y": self._calculate_return_period(hist_1y, 365)
            }
            
            # Calcular volatilidade
            daily_returns = hist_1y['Close'].pct_change().dropna()
            volatility_annual = daily_returns.std() * (252 ** 0.5) * 100
            
            # Calcular métricas avançadas
            max_price_1y = hist_1y['High'].max()
            min_price_1y = hist_1y['Low'].min()
            current_price = hist_1y['Close'].iloc[-1]
            
            # Distância dos máximos e mínimos
            distance_from_high = ((current_price - max_price_1y) / max_price_1y) * 100
            distance_from_low = ((current_price - min_price_1y) / min_price_1y) * 100
            
            return {
                **returns,
                "volatility_annual": round(volatility_annual, 2),
                "max_price_1y": round(max_price_1y, 2),
                "min_price_1y": round(min_price_1y, 2),
                "distance_from_high_pct": round(distance_from_high, 2),
                "distance_from_low_pct": round(distance_from_low, 2),
                "avg_volume_1y": round(hist_1y['Volume'].mean(), 0),
                "avg_volume_3m": round(hist_3m['Volume'].mean(), 0) if not hist_3m.empty else 0,
                "avg_volume_1m": round(hist_1m['Volume'].mean(), 0) if not hist_1m.empty else 0,
                "trading_sessions_1y": len(hist_1y)
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados históricos para {ticker}: {e}")
            return {"error": str(e)}
    
    async def _get_yfinance_dividends(self, fii, ticker: str) -> Dict[str, Any]:
        """Busca e analisa dados de dividendos do yfinance"""
        try:
            # Buscar dividendos dos últimos 2 anos
            dividends = fii.dividends
            
            if dividends.empty:
                return {"error": "Dados de dividendos não disponíveis", "annual_yield": 0.0}
            
            # Filtrar últimos 12 meses
            one_year_ago = datetime.now() - timedelta(days=365)
            recent_dividends = dividends[dividends.index >= one_year_ago]
            
            if recent_dividends.empty:
                return {"error": "Nenhum dividendo nos últimos 12 meses", "annual_yield": 0.0}
            
            # Calcular yield anual
            annual_dividends = recent_dividends.sum()
            current_price = fii.info.get('regularMarketPrice', fii.info.get('currentPrice', 1))
            annual_yield = (annual_dividends / current_price) * 100 if current_price > 0 else 0
            
            # Análise de frequência de pagamentos
            monthly_distribution = recent_dividends.groupby(recent_dividends.index.to_period('M')).sum()
            avg_monthly_dividend = monthly_distribution.mean()
            dividend_consistency = len(monthly_distribution) / 12  # % dos meses com dividendos
            
            return {
                "annual_yield": round(annual_yield, 2),
                "total_dividends_12m": round(annual_dividends, 4),
                "avg_monthly_dividend": round(avg_monthly_dividend, 4),
                "dividend_frequency": len(recent_dividends),
                "consistency_score": round(dividend_consistency, 2),
                "last_dividend_date": recent_dividends.index[-1].strftime("%Y-%m-%d") if len(recent_dividends) > 0 else None,
                "last_dividend_value": round(recent_dividends.iloc[-1], 4) if len(recent_dividends) > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar dividendos para {ticker}: {e}")
            return {"error": str(e), "annual_yield": 0.0}
    
    def _calculate_return_period(self, hist_data: pd.DataFrame, days: int) -> float:
        """Calcula retorno para um período específico com tratamento de erros"""
        try:
            if len(hist_data) < days:
                return 0.0
            
            current_price = hist_data['Close'].iloc[-1]
            past_price = hist_data['Close'].iloc[-days] if days < len(hist_data) else hist_data['Close'].iloc[0]
            
            if past_price == 0:
                return 0.0
            
            return round(((current_price - past_price) / past_price) * 100, 2)
        except:
            return 0.0
    
    def _calculate_enhanced_metrics(self, info: Dict, historical_data: Dict) -> Dict[str, Any]:
        """Calcula métricas avançadas do FII"""
        try:
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            market_cap = info.get('marketCap', 0)
            
            return {
                "liquidity_score": self._calculate_liquidity_score(info, historical_data),
                "price_stability": self._calculate_price_stability(historical_data),
                "market_cap_category": self._categorize_market_cap(market_cap),
                "performance_score": self._calculate_performance_score(historical_data),
                "risk_rating": self._calculate_risk_rating(historical_data)
            }
        except Exception as e:
            logger.error(f"Erro ao calcular métricas avançadas: {e}")
            return {}
    
    def _calculate_liquidity_score(self, info: Dict, historical_data: Dict) -> str:
        """Calcula score de liquidez"""
        avg_volume = historical_data.get('avg_volume_3m', 0)
        
        if avg_volume > 1000000:
            return "Alta"
        elif avg_volume > 100000:
            return "Média"
        elif avg_volume > 10000:
            return "Baixa"
        else:
            return "Muito Baixa"
    
    def _calculate_price_stability(self, historical_data: Dict) -> str:
        """Calcula estabilidade de preço"""
        volatility = historical_data.get('volatility_annual', 0)
        
        if volatility < 15:
            return "Muito Estável"
        elif volatility < 25:
            return "Estável"
        elif volatility < 35:
            return "Moderada"
        else:
            return "Volátil"
    
    def _categorize_market_cap(self, market_cap: float) -> str:
        """Categoriza o FII por valor de mercado"""
        if market_cap > 5000000000:  # > 5 bilhões
            return "Grande"
        elif market_cap > 1000000000:  # > 1 bilhão
            return "Médio"
        elif market_cap > 200000000:  # > 200 milhões
            return "Pequeno"
        else:
            return "Micro"
    
    def _calculate_performance_score(self, historical_data: Dict) -> str:
        """Calcula score de performance"""
        returns_1y = historical_data.get('returns_1y', 0)
        
        if returns_1y > 20:
            return "Excelente"
        elif returns_1y > 10:
            return "Bom"
        elif returns_1y > 0:
            return "Regular"
        else:
            return "Ruim"
    
    def _calculate_risk_rating(self, historical_data: Dict) -> str:
        """Calcula rating de risco"""
        volatility = historical_data.get('volatility_annual', 0)
        max_drawdown = abs(historical_data.get('distance_from_high_pct', 0))
        
        risk_score = (volatility * 0.6) + (max_drawdown * 0.4)
        
        if risk_score < 15:
            return "Baixo"
        elif risk_score < 30:
            return "Moderado"
        else:
            return "Alto"
    
    async def _get_brapi_fallback(self, ticker: str) -> Dict[str, Any]:
        """Fallback para brapi.dev quando yfinance falha"""
        try:
            params = {}
            if self.brapi_api_key:
                params['token'] = self.brapi_api_key
            
            url = f"{self.brapi_base_url}/quote/{ticker}"
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    fii_data = data['results'][0]
                    
                    return {
                        "ticker": ticker,
                        "current_price": fii_data.get('regularMarketPrice', 0),
                        "change_percent": fii_data.get('regularMarketChangePercent', 0),
                        "volume": fii_data.get('regularMarketVolume', 0),
                        "market_cap": fii_data.get('marketCap', 0),
                        "dividend_yield": fii_data.get('dividendYield', 0),
                        "p_vp": fii_data.get('priceToBook', 0),
                        "fifty_two_week_high": fii_data.get('fiftyTwoWeekHigh', 0),
                        "fifty_two_week_low": fii_data.get('fiftyTwoWeekLow', 0),
                        "average_volume": fii_data.get('averageDailyVolume10Day', 0),
                        "last_updated": datetime.now().isoformat(),
                        "source": "brapi_fallback",
                        "data_quality": "limited"
                    }
            
            logger.error(f"❌ Fallback brapi.dev também falhou para {ticker}")
            return {"error": "Nenhuma fonte de dados disponível"}
            
        except Exception as e:
            logger.error(f"❌ Erro no fallback brapi.dev para {ticker}: {e}")
            return {"error": f"Erro em todas as fontes de dados: {e}"}
    
    async def get_market_comparison(self, ticker: str) -> Dict[str, Any]:
        """Busca dados de comparação com outros FIIs do mercado"""
        try:
            # Lista de FIIs populares para comparação
            comparison_fiis = [
                "HGLG11", "VISC11", "BCFF11", "XPLG11", "MXRF11",
                "KNRI11", "BTLG11", "GGRC11", "XPML11", "RECT11"
            ]
            
            # Remover o ticker atual da comparação
            if ticker in comparison_fiis:
                comparison_fiis.remove(ticker)
            
            # Buscar dados dos FIIs de comparação
            comparison_data = []
            for fii_ticker in comparison_fiis[:5]:  # Limitar a 5 para performance
                try:
                    fii_data = await self.get_fii_data(fii_ticker)
                    if 'error' not in fii_data and fii_data.get('dividend_yield', 0) > 0:
                        comparison_data.append({
                            'ticker': fii_ticker,
                            'dividend_yield': fii_data.get('dividend_yield', 0),
                            'p_vp': fii_data.get('p_vp', 0),
                            'current_price': fii_data.get('current_price', 0)
                        })
                except Exception as e:
                    logger.warning(f"Erro ao buscar dados de {fii_ticker} para comparação: {e}")
                    continue
            
            if not comparison_data:
                return {
                    "error": "Não foi possível obter dados de comparação",
                    "avg_dividend_yield": 0.0,
                    "avg_p_vp": 0.0,
                    "market_median_dy": 0.0
                }
            
            # Calcular estatísticas do mercado
            valid_dys = [fii['dividend_yield'] for fii in comparison_data if fii['dividend_yield'] > 0]
            valid_pvps = [fii['p_vp'] for fii in comparison_data if fii['p_vp'] > 0]
            
            avg_dy = np.mean(valid_dys) if valid_dys else 0.0
            avg_pvp = np.mean(valid_pvps) if valid_pvps else 0.0
            median_dy = np.median(valid_dys) if valid_dys else 0.0
            
            return {
                "avg_dividend_yield": round(avg_dy, 2),
                "avg_p_vp": round(avg_pvp, 3),
                "market_median_dy": round(median_dy, 2),
                "sample_size": len(comparison_data),
                "comparison_fiis": [fii['ticker'] for fii in comparison_data],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar comparação de mercado: {e}")
            return {
                "error": str(e),
                "avg_dividend_yield": 0.0,
                "avg_p_vp": 0.0,
                "market_median_dy": 0.0
            }
    
    async def get_sector_analysis(self, fii_type: str = "Híbrido") -> Dict[str, Any]:
        """Análise setorial básica"""
        return {
            "sector": fii_type,
            "outlook": "Neutro",
            "key_trends": ["Crescimento do setor logístico", "Recuperação dos shoppings"],
            "risk_factors": ["Taxa de juros", "Inadimplência"],
            "last_updated": datetime.now().isoformat()
        }

# Instância global
enhanced_market_provider = EnhancedMarketDataProvider()

# Manter compatibilidade com versão anterior
market_provider = enhanced_market_provider