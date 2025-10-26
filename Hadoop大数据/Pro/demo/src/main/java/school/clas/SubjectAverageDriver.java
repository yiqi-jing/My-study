package school.clas;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

public class SubjectAverageDriver {
    public static void main(String[] args) throws Exception {
        // 配置 Hadoop 作业
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf);

        // 设置主类
        job.setJarByClass(SubjectAverageDriver.class);

        // 设置 Mapper 和 Reducer 类
        job.setMapperClass(SubjectAverageMapper.class);
        job.setReducerClass(SubjectAverageReducer.class);

        // 设置 Mapper 输出键值对类型
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(IntWritable.class);

        // 设置 Reducer 输出键值对类型
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // 设置输入和输出路径
        FileInputFormat.setInputPaths(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // 提交作业
        System.exit(job.waitForCompletion(true) ? 0 : 1);
    }
}
