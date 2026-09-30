import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    """(Conv2d => BatchNorm => ReLU) * 2"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, padding_mode='reflect'),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, padding_mode='reflect'),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        # Use Bilinear interpolation for upsampling (avoids checkerboard artifacts compared to ConvTranspose)
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # Handle asymmetric padding natively if H/W are odd
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        
        # Concatenate skip connections
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class TCResUNet(nn.Module):
    def __init__(self, in_channels=49, out_channels=15, base_c=32):
        """
        Temporal-Channel ResUNet optimized for RTX 3060 local GPU bounds natively.
        By default, collapses (7 days * 7 surface variables) = 49 input channels.
        Produces 15 continuous depth predictions.
        """
        super(TCResUNet, self).__init__()
        
        self.inc = DoubleConv(in_channels, base_c)
        self.down1 = Down(base_c, base_c*2)
        self.down2 = Down(base_c*2, base_c*4)
        self.down3 = Down(base_c*4, base_c*8)
        
        # Decoder 
        self.up1 = Up(base_c*12, base_c*4)  # (base_c*8 upsampled) + (base_c*4 skip) = 12
        self.up2 = Up(base_c*6, base_c*2)   # (base_c*4 upsampled) + (base_c*2 skip) = 6 
        self.up3 = Up(base_c*3, base_c)     # (base_c*2 upsampled) + (base_c skip) = 3
        
        self.outc = nn.Conv2d(base_c, out_channels, kernel_size=1)

    def forward(self, x):
        # Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        
        # Decoder
        x = self.up1(x4, x3)
        x = self.up2(x, x2)
        x = self.up3(x, x1)
        
        out = self.outc(x)
        return out
