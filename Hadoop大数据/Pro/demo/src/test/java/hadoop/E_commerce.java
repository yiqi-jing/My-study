package hadoop;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.*;
import org.junit.Before;
import org.junit.Test;
import java.io.IOException;

public class E_commerce {
    FileSystem fs = null;

    @Before
    public void init() throws IOException {
        // 构建配置参数对象：Configuration
        Configuration conf = new Configuration();
        // 设置参数，指定要访问的文件系统的类型：HDFS文件系统
        conf.set("fs.defaultFS", "hdfs://node1:9000");
        // 设置客户端的访问身份，以root身份访问HDFS
        System.setProperty("HADOOP_USER_NAME", "root");
        // 通过FileSystem类静态方法，获取客户端访问对象
        fs = FileSystem.get(conf);
    }

    /*创造目录 */
    @Test
    public void rawDirectory() throws IOException {
        // 创建目录
        Path dirPath = new Path("/user/retail/raw_data");
        if (!fs.exists(dirPath)) {
            fs.mkdirs(dirPath);
            System.out.println("目录创建成功：" + dirPath);
        } else {
            System.out.println("目录已存在：" + dirPath);
        }
        fs.close();
    }

    @Test
    public void analysisctory() throws IOException {
        // 创建目录 
        Path dirPath = new Path("/user/retail/analysis"); 
        if (!fs.exists(dirPath)) {
            fs.mkdirs(dirPath);
            System.out.println("目录创建成功：" + dirPath);
        } else {
            System.out.println("目录已存在：" + dirPath);
        }
        fs.close();
    }

    /* 上传原始数据 */
    @Test
    public void uploadRawData() throws IOException {
        // 创建本地上传路径的Path对象
        Path src = new Path("F:/Hadoop_data/sj/retail_data.csv");
        Path dst = new Path("/user/retail/raw_data/retail_data.csv");
        // 上传文件
        fs.copyFromLocalFile(src, dst);
        // 关闭资源
        fs.close();
        System.out.println("原始数据上传成功：" + dst);
    }

    /* 验证数据完整性 */
    @Test
    public void verifyRawData() throws IOException {
        Path dirPath = new Path("/user/retail/raw_data");
        if (fs.exists(dirPath)) {
            FileStatus[] fileStatuses = fs.listStatus(dirPath);
            System.out.println("目录内容:");
            for (FileStatus fileStatus : fileStatuses) {
                System.out.println("文件名: " + fileStatus.getPath().getName());
                System.out.println("文件大小: " + fileStatus.getLen());
                System.out.println("-----------------------------");
            }
        } else {
            System.out.println("目录不存在: " + dirPath);
        }
        fs.close();
    }
}