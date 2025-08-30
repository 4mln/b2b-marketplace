"""
Iran Payment Providers Integration
Supports major Iranian payment gateways and banks
"""
import httpx
import hashlib
import hmac
import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)

class BaseIranPaymentProvider:
    """Base class for Iran payment providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("api_key")
        self.merchant_id = config.get("merchant_id")
        self.callback_url = config.get("callback_url")
        self.is_test_mode = config.get("is_test_mode", True)
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create a payment request"""
        raise NotImplementedError
        
    async def verify_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        """Verify a payment"""
        raise NotImplementedError
        
    async def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        """Refund a payment"""
        raise NotImplementedError

class ZarinPalProvider(BaseIranPaymentProvider):
    """ZarinPal payment gateway integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.zarinpal.com/pg/v4/pay" if not self.is_test_mode else "https://sandbox.zarinpal.com/pg/v4/pay"
        self.verify_url = "https://api.zarinpal.com/pg/v4/payment/verify.json" if not self.is_test_mode else "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create ZarinPal payment request"""
        try:
            payload = {
                "merchant_id": self.merchant_id,
                "amount": int(amount),  # ZarinPal expects amount in Tomans
                "description": description,
                "callback_url": self.callback_url,
                "metadata": {
                    "reference_id": reference_id,
                    "user_phone": user_phone
                }
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.base_url, json=payload)
                data = response.json()
                
                if data.get("data", {}).get("code") == 100:
                    authority = data["data"]["authority"]
                    payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
                    
                    return {
                        "success": True,
                        "authority": authority,
                        "payment_url": payment_url,
                        "provider_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("errors", {}).get("message", "Unknown error"),
                        "provider_response": data
                    }
                    
        except Exception as e:
            logger.error(f"ZarinPal payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }
    
    async def verify_payment(self, authority: str, amount: float) -> Dict[str, Any]:
        """Verify ZarinPal payment"""
        try:
            payload = {
                "merchant_id": self.merchant_id,
                "authority": authority,
                "amount": int(amount)
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.verify_url, json=payload)
                data = response.json()
                
                if data.get("data", {}).get("code") == 100:
                    return {
                        "success": True,
                        "transaction_id": data["data"]["ref_id"],
                        "amount": data["data"]["amount"],
                        "provider_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("errors", {}).get("message", "Verification failed"),
                        "provider_response": data
                    }
                    
        except Exception as e:
            logger.error(f"ZarinPal payment verification error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }

class MellatProvider(BaseIranPaymentProvider):
    """Mellat Bank payment gateway integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.terminal_id = config.get("terminal_id")
        self.username = config.get("username")
        self.password = config.get("password")
        self.base_url = "https://bpm.shaparak.ir/pgwchannel/services/pgw" if not self.is_test_mode else "https://banktest.ir/gateway/mellat"
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create Mellat payment request"""
        try:
            # Mellat uses SOAP API, simplified implementation
            payload = {
                "terminalId": self.terminal_id,
                "userName": self.username,
                "userPassword": self.password,
                "orderId": reference_id,
                "amount": int(amount),
                "localDate": datetime.now().strftime("%Y%m%d"),
                "localTime": datetime.now().strftime("%H%M%S"),
                "additionalData": description,
                "callBackUrl": self.callback_url,
                "payerId": user_phone or "0"
            }
            
            # In real implementation, you'd use SOAP client
            # For now, return mock response
            return {
                "success": True,
                "ref_id": f"mellat_{reference_id}",
                "payment_url": f"{self.base_url}/payment?ref={reference_id}",
                "provider_response": payload
            }
            
        except Exception as e:
            logger.error(f"Mellat payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }

class ParsijooProvider(BaseIranPaymentProvider):
    """Parsijoo payment gateway integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://pay.parsijoo.ir/api/v1" if not self.is_test_mode else "https://sandbox.parsijoo.ir/api/v1"
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create Parsijoo payment request"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "amount": int(amount),
                "description": description,
                "callback_url": self.callback_url,
                "order_id": reference_id,
                "mobile": user_phone
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/payment/request",
                    json=payload,
                    headers=headers
                )
                data = response.json()
                
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "payment_id": data["data"]["payment_id"],
                        "payment_url": data["data"]["payment_url"],
                        "provider_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Payment creation failed"),
                        "provider_response": data
                    }
                    
        except Exception as e:
            logger.error(f"Parsijoo payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }

class PaypingProvider(BaseIranPaymentProvider):
    """Payping payment gateway integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.payping.ir/v2" if not self.is_test_mode else "https://sandbox.payping.ir/v2"
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create Payping payment request"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "amount": int(amount),
                "returnUrl": self.callback_url,
                "clientRefId": reference_id,
                "description": description,
                "payerIdentity": user_phone
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/pay",
                    json=payload,
                    headers=headers
                )
                data = response.json()
                
                if "code" in data:
                    payment_url = f"https://api.payping.ir/v2/pay/gotoipg/{data['code']}"
                    return {
                        "success": True,
                        "code": data["code"],
                        "payment_url": payment_url,
                        "provider_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("message", "Payment creation failed"),
                        "provider_response": data
                    }
                    
        except Exception as e:
            logger.error(f"Payping payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }

class IDPayProvider(BaseIranPaymentProvider):
    """IDPay payment gateway integration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.idpay.ir/v1.1" if not self.is_test_mode else "https://api.idpay.ir/v1.1"
        
    async def create_payment(self, amount: float, currency: str, description: str, 
                           reference_id: str, user_phone: str = None) -> Dict[str, Any]:
        """Create IDPay payment request"""
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "X-SANDBOX": "1" if self.is_test_mode else "0",
                "Content-Type": "application/json"
            }
            
            payload = {
                "order_id": reference_id,
                "amount": int(amount),
                "name": "B2B Marketplace",
                "phone": user_phone,
                "mail": "user@example.com",
                "desc": description,
                "callback": self.callback_url
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/payment",
                    json=payload,
                    headers=headers
                )
                data = response.json()
                
                if data.get("status") == 200:
                    return {
                        "success": True,
                        "id": data["id"],
                        "link": data["link"],
                        "provider_response": data
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("error_message", "Payment creation failed"),
                        "provider_response": data
                    }
                    
        except Exception as e:
            logger.error(f"IDPay payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider_response": None
            }

# Payment provider factory
class IranPaymentFactory:
    """Factory for creating Iran payment providers"""
    
    @staticmethod
    def create_provider(provider_name: str, config: Dict[str, Any]) -> BaseIranPaymentProvider:
        """Create payment provider instance"""
        providers = {
            "zarinpal": ZarinPalProvider,
            "mellat": MellatProvider,
            "parsijoo": ParsijooProvider,
            "payping": PaypingProvider,
            "idpay": IDPayProvider
        }
        
        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unsupported payment provider: {provider_name}")
            
        return provider_class(config)

# Utility functions
async def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """Get list of available payment providers with their configurations"""
    return {
        "zarinpal": {
            "name": "ZarinPal",
            "display_name": "زرین‌پال",
            "description": "Most popular Iranian payment gateway",
            "supports_irr": True,
            "supports_usd": False,
            "supports_eur": False,
            "transaction_fee_percentage": 1.0,
            "minimum_amount": 1000,
            "logo_url": "/static/images/payment/zarinpal.png"
        },
        "mellat": {
            "name": "Mellat Bank",
            "display_name": "بانک ملت",
            "description": "Official Mellat Bank payment gateway",
            "supports_irr": True,
            "supports_usd": False,
            "supports_eur": False,
            "transaction_fee_percentage": 0.5,
            "minimum_amount": 1000,
            "logo_url": "/static/images/payment/mellat.png"
        },
        "parsijoo": {
            "name": "Parsijoo",
            "display_name": "پارس‌ایجو",
            "description": "Fast and reliable payment gateway",
            "supports_irr": True,
            "supports_usd": False,
            "supports_eur": False,
            "transaction_fee_percentage": 1.5,
            "minimum_amount": 1000,
            "logo_url": "/static/images/payment/parsijoo.png"
        },
        "payping": {
            "name": "Payping",
            "display_name": "پی‌پینگ",
            "description": "Modern payment gateway with good UX",
            "supports_irr": True,
            "supports_usd": False,
            "supports_eur": False,
            "transaction_fee_percentage": 1.0,
            "minimum_amount": 1000,
            "logo_url": "/static/images/payment/payping.png"
        },
        "idpay": {
            "name": "IDPay",
            "display_name": "آیدی‌پی",
            "description": "Secure payment gateway with fraud protection",
            "supports_irr": True,
            "supports_usd": False,
            "supports_eur": False,
            "transaction_fee_percentage": 1.2,
            "minimum_amount": 1000,
            "logo_url": "/static/images/payment/idpay.png"
        }
    }

async def calculate_payment_fees(amount: float, provider_name: str) -> Dict[str, float]:
    """Calculate payment fees for a given amount and provider"""
    providers = await get_available_providers()
    provider = providers.get(provider_name.lower())
    
    if not provider:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    fee_percentage = provider["transaction_fee_percentage"]
    fee_amount = (amount * fee_percentage) / 100
    
    return {
        "amount": amount,
        "fee_percentage": fee_percentage,
        "fee_amount": fee_amount,
        "total_amount": amount + fee_amount
    }
