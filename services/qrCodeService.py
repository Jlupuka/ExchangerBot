import asyncio
import datetime
import pathlib

import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.main import QRCode

from CastomExceptions.castomException import NotFoundCryptoToken


class QRCodeService:
    @staticmethod
    async def create_crypto_payment_qrcode(crypto_currency: str, amount: float,
                                           address: str, description: str | int = None) -> str:
        match crypto_currency:
            case 'BTC':
                payment_link = f'bitcoin:{address}?amount={amount}'
            case 'ETH':
                payment_link = f'ethereum:{address}?value={amount}'
            case 'XMR':
                payment_link = f'monero:{address}?tx_amount={amount}&tx_description={description}'
            case 'TRX':
                payment_link = f'tron:{address}?amount={amount}'
            case 'DOGE':
                payment_link = f'doge:{address}?amount={amount}'
            case _:
                raise NotFoundCryptoToken(f'The network {crypto_currency} is not in the system')
        qr: QRCode = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_link)
        qr.make(fit=True)
        await QRCodeService.create_directory('tempQRCode')
        file_name = f'tempQRCode/{crypto_currency}_{amount}_{address}_{datetime.datetime.now()}.png'
        qr.make_image(image_factory=StyledPilImage,
                      color_mask=RadialGradiantColorMask(),
                      module_drawer=RoundedModuleDrawer(radius_ratio=1)).save(file_name)
        return file_name

    @staticmethod
    async def delete_file(file_name: str) -> None:
        file_path = pathlib.Path(file_name)
        if file_path.exists() and file_path.is_file():
            await asyncio.get_event_loop().run_in_executor(None, file_path.unlink)

    @staticmethod
    async def create_directory(directory_name: str) -> None:
        directory_path = pathlib.Path(directory_name)
        if not directory_path.exists():
            await asyncio.get_event_loop().run_in_executor(None, directory_path.mkdir)
