package school.clas;

import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

import java.io.IOException;

public class SubjectAverageMapper extends Mapper<Object, Text, Text, IntWritable> {
    @Override
    protected void map(Object key, Text value, Context context) throws IOException, InterruptedException {
        // 按行读取数据
        String line = value.toString();
        // 按制表符或逗号分隔字段
        String[] fields = line.split(",");
        // 获取科目和成绩
        String course = fields[1]; // 假设科目在第二列
        int grade = Integer.parseInt(fields[2]); // 假设成绩在第三列
        // 输出键值对 <科目, 成绩>
        context.write(new Text(course), new IntWritable(grade));
    }
}