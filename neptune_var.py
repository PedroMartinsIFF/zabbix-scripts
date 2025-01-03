# Arquivo com os parametros de variaveis

def get_data(database,value):
    if value == 0:
        data_instance = {
                    'Id': 'm1',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'LoaderRequestsPerSec',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm2',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'EngineUptime',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm3',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'CPUUtilization',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm4',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'BufferCacheHitRatio',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm5',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'MainRequestQueuePendingRequests',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm6',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'FreeableMemory',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm7',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'ClusterReplicaLag',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm8',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'TotalRequestsPerSec',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm9',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'TotalServerErrorsPerSec',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm10',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'TotalClientErrorsPerSec',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm11',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'NumTxCommitted',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm12',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'NumTxOpened',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm13',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'NumTxRolledBack',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm14',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'SparqlRequestsPerSec',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },
        return data_instance
    else:
        data_cluster = {
                    'Id': 'm15',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'VolumeReadIOPs',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm16',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'VolumeWriteIOPs',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm17',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'VolumeBytesUsed',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm18',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'TotalBackupStorageBilled',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm19',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'SnapshotStorageUsed',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },{
                    'Id': 'm20',
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/Neptune',
                            'MetricName': 'BackupRetentionPeriodStorageUsed',
                            'Dimensions': [
                                {
                                    'Name': 'DBClusterIdentifier',
                                    'Value': database
                                },
                            ]
                        },
                        'Period': 60,
                        'Stat': 'Average',
                    },
                },
        return data_cluster
