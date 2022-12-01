stats_post_ref_q = """\
    query StatsPostReferrersContainer($postId: ID!) {
        post(id: $postId) {
            id
            ...StatsPostReferrersExternalRow_post
            referrers {
              ...StatsPostReferrersContainer_referrers
              __typename
            }
            totalStats {
              ...StatsPostReferrersAll_totalStats
              __typename
            }
            __typename
        }
    }
    fragment StatsPostReferrersExternalRow_post on Post {
      title
      __typename
    }
    fragment StatsPostReferrersContainer_referrers on Referrer {
      postId
      sourceIdentifier
      totalCount
      type
      internal {
        postId
        collectionId
        profileId
        type
        __typename
      }
      search {
        domain
        keywords
        __typename
      }
      site {
        href
        title
        __typename
      }
      platform
      __typename
    }
    fragment StatsPostReferrersAll_totalStats on SummaryPostStat {
      views
      __typename
    }
"""
