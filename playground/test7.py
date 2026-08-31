class Solution:
    def longestCommonPrefix(self, strs: list[str]) -> str:
        """
        
        """
        if len(strs)==0:
            return ""

        if len(strs)==1:
            return strs[0]

        common_prefix = strs[0]

        for i in range(1,len(strs)):

            while strs[i].startswith(common_prefix) is False and len(common_prefix)>0:
                common_prefix = common_prefix[:-1]

            if len(common_prefix)==0:
                return ''

        return common_prefix




a = Solution()

strs = ["flower","flow","flight"]


b = a.longestCommonPrefix(strs)

print(b)