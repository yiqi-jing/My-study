package school.clas;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

import java.io.IOException;

public class SubjectAverageReducer extends Reducer<Text, IntWritable, Text, Text> {
    @Override
    protected void reduce(Text key, Iterable<IntWritable> values, Context context) throws IOException, InterruptedException {
        int totalScore = 0;
        int count = 0;
        // 遍历成绩，累加总分并统计人数
        for (IntWritable value : values) {
            totalScore += value.get();
            count++;
        }
        // 计算平均分
        double average = totalScore / (double) count;
        // 输出键值对 <科目, 平均分>
        context.write(key, new Text(String.format("%.2f", average)));
    }
}