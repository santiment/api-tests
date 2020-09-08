queries = {
    "historyPrice": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "marketcap",
            "priceBtc",
            "priceUsd",
            "volume"
        ]
    },
    "ohlc": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "closePriceUsd",
            "highPriceUsd",
            "lowPriceUsd",
            "openPriceUsd"
        ]
    },
    "priceVolumeDiff": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"',
            "currency": '"USD"'
        },
        "fields": [
            "priceChange",
            "priceVolumeDiff",
            "volumeChange"
        ]
    },
    "devActivity": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "datetime",
            "activity"
        ]
    },
    "githubActivity": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "datetime",
            "activity"
        ]
    },
    "historyTwitterData": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "followersCount"
        ]
    },
    "twitterData": {
        "arguments": {
            "slug": '"%s"',
        },
        "fields": [
            "followersCount"
        ]
    },
    "socialGainersLosersStatus": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "timeWindow": '"10d"'
        },
        "fields": [
            "status"
        ]
    },
    "socialVolume": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"',
            "socialVolumeType": "TELEGRAM_CHATS_OVERVIEW"
        },
        "fields": [
            "mentionsCount"
        ]
    },
    "socialDominance": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "dominance"
        ]
    },
    "exchangeWallets": {
        "arguments": {
            "slug": '"%s"'
        },
        "fields": [
            "isDex"
        ]
    },
    "allExchanges": {
        "arguments": {
            "slug": '"%s"'
        },
        "fields": []
    },
    "miningPoolsDistribution": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "other",
            "top10",
            "top3"
        ]
    },
    "dailyActiveDeposits": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "datetime",
            "activeDeposits"
        ]
    },
    "gasUsed": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "ethGasUsed",
            "gasUsed"
        ]
    },
    "exchangeFundsFlow": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "datetime",
            "inOutDifference"
        ]
    },
    "historicalBalance": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"',
            "address": '"0x0000000000000000000000000000000000000000"'
        },
        "fields": [
            "balance"
        ]
    },
    "topHoldersPercentOfTotalSupply": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"',
            "numberOfHolders": "10"
        },
        "fields": [
            "inExchanges",
            "inTopHoldersTotal",
            "outsideExchanges"
        ]
    },
    "percentOfTokenSupplyOnExchanges": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "percentOnExchanges"
        ]
    },
    "shareOfDeposits": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "shareOfDeposits"
        ]
    },
    "realizedValue": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "nonExchangeRealizedValue",
            "realizedValue"
        ]
    },
    "networkGrowth": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "newAddresses"
        ]
    },
    "mvrvRatio": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "ratio"
        ]
    },
    "dailyActiveAddresses": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "activeAddresses"
        ]
    },
    "burnRate": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "burnRate"
        ]
    },
    "averageTokenAgeConsumedInDays": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "tokenAge"
        ]
    },
    "tokenVelocity": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "tokenVelocity"
        ]
    },
    "nvtRatio": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "nvtRatioCirculation",
            "nvtRatioTxVolume"
        ]
    },
    "transactionVolume": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "transactionVolume"
        ]
    },
    "tokenCirculation": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "tokenCirculation"
        ]
    },
    "getTrendingWords": {
        "arguments": {
            "size": "10",
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "topWords {score word}"
        ]
    },
    "timelineEvents": {
        "arguments": {
            "limit": "10",
        },
        "fields": [
            "events {id}"
        ]
    },
    "topSocialGainersLosers": {
        "arguments": {
            "size": "1",
            "status": "ALL",
            "from": '"%s"',
            "to": '"%s"',
            "timeWindow": '"2d"'
        },
        "fields": [
            " projects {change slug status}"
        ]
    },
    "minersBalance": {
        "arguments": {
            "slug": '"%s"',
            "from": '"%s"',
            "to": '"%s"',
            "interval": '"%s"'
        },
        "fields": [
            "balance"
        ]
    },
    "featuredInsights": {
        "arguments": {},
        "fields": [
            """
       id
    readyState
    title
    createdAt
    publishedAt
    updatedAt
    tags {
      name
    }
    votedAt
    votes {
      totalVotes
    }
    user {
      id
      username
      avatarUrl
    }
    shortDesc
    commentsCount
    isPaywallRequired
    isPulse
    __typename
    """
        ]
    },
     "featuredWatchlists": {
        "arguments": {},
        "fields": [
            """
            id
    isPublic
    name
    function
    insertedAt
    isMonitored
    updatedAt
    user {
      id
    }
       listItems {
      project {
        id
        slug
      }
    }
    """
        ]
    },
     "featuredChartConfigurations": {
        "arguments": {},
        "fields": [
            """
            id
    isPublic
    title
    description
    metrics
    project {
      id
      slug
      name
      ticker
    }
    user {
      id
      avatarUrl
      username
    }
    options
    insertedAt
    __typename
    """
        ]
    },
    "getReports": {
        "arguments": {},
        "fields": [
            "description",
            "name",
            "url"
        ]
    }
}

special_queries = [
    "averageDevActivity",
    "averageGithubActivity",
    "tokenTopTransactions",
    "ethSpentOverTime",
    "ethTopTransactions",
    "ethBalance",
    "usdBalance",
    "icos",
    "icoPrice",
    "initialIco",
    "fundsRaisedUsdIcoEndPrice",
    "fundsRaisedEthIcoEndPrice",
    "fundsRaisedBtcIcoEndPrice",
    "tokenAgeConsumed",
    "ethSpent",
    "socialGainersLosersStatus",
    "exchangeWallets",
    "allExchanges",
    "percentOfTokenSupplyOnExchanges",
    "dailyActiveDeposits",
    "shareOfDeposits",
    "social_active_users"
]
