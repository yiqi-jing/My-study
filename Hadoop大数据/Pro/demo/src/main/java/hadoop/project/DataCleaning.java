package hadoop.project;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Counters;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

import java.io.IOException;

public class DataCleaning {

    /**
     * Mapper类：数据清洗核心逻辑
     * 功能：实现多字段验证并统计清洗率
     */
    public static class DataCleaningMapper extends Mapper<LongWritable, Text, Text, NullWritable> {
        // 字段索引定义（从0开始）
        private static final int CUSTOMER_ID_INDEX = 1;
        private static final int NAME_INDEX = 2;
        private static final int AGE_INDEX = 10;
        private static final int AMOUNT_INDEX = 18;
        private static final int PRODUCT_CATEGORY_INDEX = 19;
        private static final int PAYMENT_METHOD_INDEX = 24;
        private static final int ORDER_STATUS_INDEX = 25;

        // 自定义计数器枚举
        public static enum CLEANING_COUNTERS {
            TOTAL_RECORDS,       // 总记录数
            VALID_RECORDS,       // 有效记录数
            INVALID_CUSTOMER_ID, // 无效客户ID
            INVALID_NAME,        // 无效姓名
            INVALID_AGE,         // 无效年龄
            INVALID_AMOUNT,      // 无效金额
            INVALID_CATEGORY,    // 无效产品类别
            INVALID_PAYMENT,     // 无效支付方式
            INVALID_STATUS       // 无效订单状态
        }

        private Text outputRecord = new Text();

        @Override
        protected void map(LongWritable key, Text value, Context context)
                throws IOException, InterruptedException {
            
            // 总记录数统计
            context.getCounter(CLEANING_COUNTERS.TOTAL_RECORDS).increment(1);
            
            String line = value.toString().trim();
            if (line.isEmpty()) return;

            String[] fields = line.split(",", -1);

            /* ========== 多字段验证逻辑 ========== */
            
            // 1. 客户ID验证
            if (fields[CUSTOMER_ID_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_CUSTOMER_ID).increment(1);
                return;
            }

            // 2. 客户姓名验证
            if (fields[NAME_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_NAME).increment(1);
                return;
            }

            // 3. 年龄验证
            try {
                int age = Integer.parseInt(fields[AGE_INDEX].trim());
                if (age <= 0 || age > 120) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_AGE).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_AGE).increment(1);
                return;
            }

            // 4. 金额验证
            try {
                double amount = Double.parseDouble(fields[AMOUNT_INDEX].trim());
                if (amount <= 0) {
                    context.getCounter(CLEANING_COUNTERS.INVALID_AMOUNT).increment(1);
                    return;
                }
            } catch (NumberFormatException e) {
                context.getCounter(CLEANING_COUNTERS.INVALID_AMOUNT).increment(1);
                return;
            }

            // 5. 产品类别验证
            if (fields[PRODUCT_CATEGORY_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_CATEGORY).increment(1);
                return;
            }

            // 6. 支付方式验证
            if (fields[PAYMENT_METHOD_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_PAYMENT).increment(1);
                return;
            }

            // 7. 订单状态验证
            if (fields[ORDER_STATUS_INDEX].trim().isEmpty()) {
                context.getCounter(CLEANING_COUNTERS.INVALID_STATUS).increment(1);
                return;
            }

            /* ========== 输出有效记录 ========== */
            context.getCounter(CLEANING_COUNTERS.VALID_RECORDS).increment(1);
            outputRecord.set(line);
            context.write(outputRecord, NullWritable.get());
        }
    }

    /**
     * 主程序入口
     */
    public static void main(String[] args) throws Exception {
        // ==================== 用户界面 ====================
        System.out.println("╔════════════════════════════════════════╗");
        System.out.println("║      大数据清洗工具 - 全字段数据清洗     ║");
        System.out.println("╚════════════════════════════════════════╝");
        System.out.println("\n【清洗规则】");
        System.out.println("1. 客户ID：非空验证");
        System.out.println("2. 客户姓名：非空验证");
        System.out.println("3. 年龄：1-120岁有效范围");
        System.out.println("4. 交易金额：正数验证");
        System.out.println("5. 产品类别：非空验证");
        System.out.println("6. 支付方式：非空验证");
        System.out.println("7. 订单状态：非空验证");
        
        // ==================== 参数检查 ====================
        if (args.length != 2) {
            System.err.println("\n【错误】参数不正确！");
            System.err.println("用法: hadoop jar DataCleaning.jar <输入路径> <输出路径>");
            System.err.println("示例: hadoop jar DataCleaning.jar /input /output");
            System.exit(1);
        }

        // ==================== 作业配置 ====================
        System.out.println("\n【作业配置】");
        System.out.println("输入路径: " + args[0]);
        System.out.println("输出路径: " + args[1]);
        
        Configuration conf = new Configuration();
        Job job = Job.getInstance(conf, "全字段数据清洗作业");
        
        job.setJarByClass(DataCleaning.class);
        job.setMapperClass(DataCleaningMapper.class);
        job.setNumReduceTasks(0);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(NullWritable.class);

        // ==================== 路径设置 ====================
        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));

        // ==================== 作业执行 ====================
        System.out.println("\n【执行状态】");
        System.out.println("正在启动数据清洗作业...");
        
        long startTime = System.currentTimeMillis();
        boolean success = job.waitForCompletion(true);
        long endTime = System.currentTimeMillis();

        // ==================== 清洗报告 ====================
        if (success) {
            Counters counters = job.getCounters();
            
            // 获取计数器值
            long total = counters.findCounter(DataCleaningMapper.CLEANING_COUNTERS.TOTAL_RECORDS).getValue();
            long valid = counters.findCounter(DataCleaningMapper.CLEANING_COUNTERS.VALID_RECORDS).getValue();
            double rate = total > 0 ? (valid * 100.0 / total) : 0;
            
            System.out.println("\n【清洗报告】");
            System.out.println("✅ 作业完成");
            System.out.printf("⏱️ 总耗时: %.2f秒\n", (endTime - startTime)/1000.0);
            System.out.println("📊 记录统计:");
            System.out.printf("  总记录数: %d\n", total);
            System.out.printf("  有效记录: %d (%.2f%%)\n", valid, rate);
            System.out.printf("  无效记录: %d (%.2f%%)\n", total - valid, 100 - rate);
            
            System.out.println("\n🔍 无效原因分析:");
            printCounter(counters, "  空客户ID: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_CUSTOMER_ID);
            printCounter(counters, "  空客户姓名: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_NAME);
            printCounter(counters, "  无效年龄: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_AGE);
            printCounter(counters, "  无效金额: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_AMOUNT);
            printCounter(counters, "  空产品类别: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_CATEGORY);
            printCounter(counters, "  空支付方式: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_PAYMENT);
            printCounter(counters, "  空订单状态: ", DataCleaningMapper.CLEANING_COUNTERS.INVALID_STATUS);
            
            System.out.println("\n📂 输出路径: " + args[1]);
        } else {
            System.out.println("❌ 作业执行失败！");
        }
        
        System.exit(success ? 0 : 1);
    }

    // 辅助方法：打印计数器信息
    private static void printCounter(Counters counters, String label, 
            DataCleaningMapper.CLEANING_COUNTERS counter) {
        long value = counters.findCounter(counter).getValue();
        if (value > 0) {
            System.out.println(label + value);
        }
    }
}
