# pymcbdsc

Pymcbdsc(Python Minecraft Bedrock Dedicated Server Container Manager (長い...)) は、 [Bedrock Dedicated Server](https://www.minecraft.net/en-us/download/server/bedrock) (以下、 BDS)を手間をかけずに構築・運用する為のスクリプト及び Python モジュールです。

Pymcbdsc には次の特徴があります。

*   BDS のアップデートを自動的に行える。
*   コンテナ技術を用いることで、環境を汚さずに BDS を構築できる。
*   定期的なセーブデータのバックアップを行える。

なお、 Pymcbdsc は非公式であり、 Minecraft 及び Mojang AB から何ら承認を得たものではありません。

## Overview

Minecraft Bedrock Edition は不定期に新バージョンがリリースされ、多くの場合は Minecraft (クライアント) が自動的にバージョンアップされます。
Minecraft Bedrock Edition の新バージョンリリースに伴い、 BDS の新バージョンもリリースされますが、残念なことにこちらを自動バージョンアップする手段は用意されていません。

Pymcbdsc では、この不便を解消するために BDS を自動バージョンアップする手段を提供します。

また、[マインクラフト エンドユーザーライセンス規約](https://account.mojang.com/terms)では Mojang AB の著作物について再頒布が禁止されています。
このため、本モジュールでは本モジュールを利用する各環境で BDS をダウンロードし使用する方式を採用しています。

## Getting Started

### Prerequisites

Docker (Windows の場合は [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)) がインストールされ、動作している必要があります。

また、 BDS をダウンロード及び利用する為に、下記の利用規約にも同意する必要があります。

*   [マインクラフト エンドユーザーライセンス規約](https://account.mojang.com/terms)
*   [プライバシーポリシー](https://privacy.microsoft.com/ja-jp/privacystatement)

### Installing

1.  Pymcbdsc をインストールします。

    ```
    pip install pymcbdsc
    ```
1.  ディレクトリ(フォルダ)やファイルを配置します。

    ```
    python -m pymcbdsc install
    ```
    または

    ```
    mcbdsc install
    ```

## Configuration

**Tag**

BDS (というか、 Minecraft) のバージョニングは `major.minor.patch.revision` となっております。
本モジュールでは、作成した Docker Image に対してこの BDS のバージョンをもとに Tag の付与を行います。

本モジュールが付与する Tag は次の3種類です。

|タグの種類|意味|例|
|----|----|----|
|latest|最新の BDS バージョンのイメージを指します。|latest|
|minor|`major.minor` 毎に作成され、各 BDS マイナーバージョンの最新イメージを指します。|1.16|
|revision|`major.minor.patch.revision` すべてを含み、各 BDS バージョンのイメージを指します。|1.16.201.02|

## Authors

*   **Kodai Tooi** [GitHub](https://github.com/ktooi), [Qiita](https://qiita.com/ktooi)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
