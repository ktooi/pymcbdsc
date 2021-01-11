# pymcbdsc

Pymcbdsc(Python Minecraft Bedrock Dedicated Server Container Manager (長い...)) は、 [Bedrock Dedicated Server](https://www.minecraft.net/en-us/download/server/bedrock) (以下、 BDS)を手間をかけずに構築・運用する為のスクリプト及び Python モジュールです。

Minecraft Bedrock Edition は不定期に新バージョンがリリースされ、多くの場合は Minecraft (クライアント) が自動的にバージョンアップされます。
Minecraft Bedrock Edition の新バージョンリリースに伴い、 BDS の新バージョンもリリースされますが、残念なことにこちらを自動バージョンアップする手段は用意されていません。

Pymcbdsc では、この不便を解消するために BDS を自動バージョンアップする手段を提供します。

Pymcbdsc には次の特徴があります。

*   BDS を自動バージョンアップできる。
*   コンテナ技術を用いることで、環境を汚さずに BDS を構築できる。
*   複数の BDS を管理でき、必要に応じてそれぞれのバージョンを固定できる。

## Getting Started

### Prerequisites

Docker (Windows の場合は [Docker Desktop for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)) がインストールされ、動作している必要があります。

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

## Authors

*   **Kodai Tooi** [GitHub](https://github.com/ktooi), [Qiita](https://qiita.com/ktooi)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
