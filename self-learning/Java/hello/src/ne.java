import java.util.List;
import java.util.ArrayList;

class Solution {

    private static final String[] MAPPING = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

    public List<String> letterCombinations(String digits) {
        List<String> ans = new ArrayList<>();
        if (digits == null || digits.isEmpty()) {
            return ans;
        }
        dfs(0, new StringBuilder(), digits, ans);
        return ans;
    }

    private void dfs(int idx, StringBuilder path, String digits, List<String> ans) {
        if (idx == digits.length()) {
            ans.add(path.toString());
            return;
        }
        String letters = MAPPING[digits.charAt(idx) - '0'];
        for (char c : letters.toCharArray()) {
            path.append(c);
            dfs(idx + 1, path, digits, ans);
            path.deleteCharAt(path.length() - 1); // 回溯
        }
    }
}
